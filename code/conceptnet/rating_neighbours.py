import configparser
import json
import time

from scipy.spatial.distance import cosine
from transformers import AutoModel, AutoTokenizer
import torch
from hopcreation import read_hop, findItOut_concepts


one_hop_cap = 32
two_hop_cap = 32
# ratio true means we take the top #one_hop_cap according to the amount of relations shared between starting concept and
# other concept divided by the total amount of neighbours the target concept has.
# false means we use just the total amount of connections and do not care about the total amount of connections the
# target concept has
ratio = True

# these values are used for the bert cosine similarity score
# the amount of each order of entries we care about
fo_limit = 16
so_limit = 16

concept_cap = 8


#
# def example():
#
#     tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
#     model = BertForMultipleChoice.from_pretrained("bert-base-uncased")
#
#     prompt = "In Italy, pizza served in formal settings, such as at a restaurant, is presented unsliced."
#     choice0 = "It is eaten with a fork and a knife."
#     choice1 = "It is eaten while held in the hand."
#     choice2 = "it is eaten with your mum."
#     labels = torch.tensor(0).unsqueeze(0)
#
#     encoding = tokenizer([prompt, prompt, prompt], [choice0, choice1, choice2], return_tensors="pt", padding=True)
#     outputs = model(**{k: v.unsqueeze(0) for k, v in encoding.items()}, labels=labels)  # batch size is 1
#
#     # the linear classifier still needs to be trained
#     loss = outputs.loss
#     logits = outputs.logits
#
#     print(labels)
#
#     print(loss)
#     print(logits)
#
#     # dict = read_hop("one_hop")
#     # print(dict["table"])
#     # func = lambda x: x[0]
#     # set1 = dict["table"][0:32].map(func)
#     # set1 = set(set1)
#     # for x in dict:
#     #     dict[x].sort(key= lambda x : x[1]/x[2], reverse=True)
#     # print(dict["table"])
#     #
#     # set2 = dict["table"][0:32].map(func)
#     # set2 = set(set2)
#     #
#     # s3 = set1.intersection(set2)
#     # print(s3)
#     # s4 = set1 - s3
#     # s5 = set2 - s3
#     #
#     # print(s4)
#     # print(s5)

def rate_bert():
    relations = prepare_questions_topics()
    count = 0
    startt = time.time()

    results = dict()
    results["first_order"] = dict()
    results["second_order"] = dict()

    print("total concepts: " , len(relations))

    for x in relations:
        if ((count < 3000000)):
            if ((relations[x].keys().__contains__("question"))):
                count = count + 1
                question = relations[x]["question"][0]["question"]
                one_hop = relations[x]["one_hop"]
                two_hop = relations[x]["two_hop"]

                if len(one_hop) > fo_limit:
                    one_hop = one_hop[0:fo_limit]
                if len(two_hop) > so_limit:
                    two_hop =  two_hop[0: so_limit]

                one_hop_rels = relations[x]["one_hop_rels"]
                two_hop_rels = relations[x]["two_hop_rels"]

                text = [question]

                missed1 = []

                map_first_order = dict()

                for rel in one_hop:
                    if(one_hop_rels.keys().__contains__(rel[0])):
                        for a in one_hop_rels[rel[0]]:
                            map_first_order[a] = rel[0]
                        text.extend(one_hop_rels[rel[0]])
                    else:
                        missed1.append(rel[0])

                bert_start_time = time.time()


                tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-bert-base-uncased")
                model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-bert-base-uncased")

                inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

                with torch.no_grad():
                    embeddings = model(**inputs, output_hidden_states=True, return_dict=True).pooler_output

                cosine_sims = []
                for i in range(len(text)):
                    if not(i == 0):
                        cosine_sims.append((text[i], 1- cosine(embeddings[0], embeddings[i])))

                #print(cosine_sims)

                cosine_sims.sort(key = lambda x : x[1], reverse=True)
                #print(cosine_sims)

                first_order_results = []

                for co in cosine_sims:
                    concept = map_first_order[co[0]]
                    if(not first_order_results.__contains__(concept)):
                        first_order_results.append(concept)




                text = [question]
                missed2 = []

                map_second_order = dict()



                for rel in two_hop:
                    if (two_hop_rels.keys().__contains__(rel[0])):
                        for a in two_hop_rels[rel[0]]:
                            map_second_order[a] = rel[0]
                        text.extend(two_hop_rels[rel[0]])
                    else:
                        missed2.append(rel[0])

                tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-bert-base-uncased")
                model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-bert-base-uncased")

                inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

                with torch.no_grad():
                    embeddings = model(**inputs, output_hidden_states=True, return_dict=True).pooler_output

                cosine_sims = []
                for i in range(len(text)):
                    if not (i == 0):
                        cosine_sims.append((text[i], 1 - cosine(embeddings[0], embeddings[i])))

                # print(cosine_sims)

                cosine_sims.sort(key=lambda x: x[1], reverse=True)
                # print(cosine_sims)

                second_order_results = []

                for co in cosine_sims:
                    concept = map_second_order[co[0]]
                    if (not second_order_results.__contains__(concept)):
                        second_order_results.append(concept)

                bert_finish_time = time.time()
                task_time = bert_finish_time - bert_start_time
                print(x + " took: " + str(task_time) + " seconds")

                results["first_order"][x] = first_order_results
                results["second_order"][x] = second_order_results



    fint = time.time()
    print("took: " + str(fint - startt) + "seconds")

    config = configparser.ConfigParser()
    config.read("paths.cfg")

    file_first = open(config["paths"]["generated_first_order"], "w", encoding="utf8")

    concepts = list(results["first_order"].keys())
    concepts.sort()

    for con in concepts:
        line = con + "\t"
        fo_concepts = results["first_order"][con]

        if(len(fo_concepts) > concept_cap):
            fo_concepts = fo_concepts[0:concept_cap]

        for tar in fo_concepts:
            line = line + "|" + tar

        file_first.write(line + "\n")

    file_second = open(config["paths"]["generated_second_order"], "w", encoding="utf8")

    concepts = list(results["second_order"].keys())
    concepts.sort()

    for con in concepts:
        line = con + "\t"
        fo_concepts = results["second_order"][con]

        if (len(fo_concepts) > concept_cap):
            fo_concepts = fo_concepts[0:concept_cap]

        for tar in fo_concepts:
            line = line + "|" + tar

        file_second.write(line + "\n")

    game_board = open(config["paths"]["generated_board"], "w", encoding="utf8")

    concepts = list(results["second_order"].keys())
    concepts.sort()

    for con in concepts:
        line = con + "\t" + relations[con]["question"][0]["question"] + "\t"
        fo_concepts = results["first_order"][con]
        so_concepts = results["second_order"][con]

        tl = len(fo_concepts) + len(so_concepts)

        concepts_final = set()

        maxl = len(fo_concepts)
        if (len(so_concepts) > maxl):
            maxl = len(so_concepts)

        for i in range(maxl):
            if(i < len(fo_concepts)):
                if(len(concepts_final) < concept_cap):
                    concepts_final.add(fo_concepts[i])

            if(i < len(so_concepts)):
                if (len(concepts_final) < concept_cap):
                    concepts_final.add(so_concepts[i])

        concepts_final = list(concepts_final)
        concepts_final.sort()

        for tar in concepts_final:
            line = line + "|" + tar

        game_board.write(line + "\n")


# returns a dictonary with topic as key, giving another dic with one_hop and two_hop
def prepare_questions_topics():
    #one_hop = read_hop("one_hop")
    #two_hop = read_hop("two_hop")

    one_hop = read_hop("first_order")
    two_hop = read_hop("second_order")

    questions = {}
    topics = findItOut_concepts()

    config = configparser.ConfigParser()
    config.read("paths.cfg")

    f = open(config["paths"]["valid_questions"], encoding="utf8")

    for line in f:
        json_obj = json.loads(line)
        # print(json_obj["answerKey"])
        question_concept = json_obj["question"]["question_concept"]
        question = json_obj["question"]["stem"]
        # question_id = json_obj["id"]
        stem = json_obj["question"]["stem"].split()
        stem_q1 = json_obj["statements"][0]["statement"].split()
        index = -1
        for x in zip(stem, stem_q1):
            index = index + 1
            if (x[0] != x[1]):
                # print(x[0])
                # print(x[1])
                # print(index)
                break
        questions[question_concept] = list()
        questions[question_concept].append(dict([("stem", stem), ("index", index), ("question", question)]))

    combined = {}
    no_topic = 0
    for topic in topics:
        combined[topic] = {}

        one_hop_rel = one_hop[topic]
        two_hop_rel = two_hop[topic]
        if (ratio):
            one_hop_rel.sort(key=lambda x: x[1] / x[2], reverse=True)
            two_hop_rel.sort(key=lambda x: x[1] / x[2], reverse=True)
        else:
            one_hop_rel.sort(key=lambda x: x[1], reverse=True)
            two_hop_rel.sort(key=lambda x: x[1], reverse=True)

        one_hop_max = one_hop_cap
        two_hop_max = two_hop_cap
        if (len(one_hop_rel) < one_hop_max):
            one_hop_max = len(one_hop_rel)
        if (len(two_hop_rel) < two_hop_max):
            two_hop_max = len(two_hop_rel)
        one_hop_rel = one_hop_rel[0:one_hop_max]
        two_hop_rel = two_hop_rel[0:two_hop_max]

        combined[topic]["one_hop"] = one_hop_rel
        combined[topic]["two_hop"] = two_hop_rel
        combined[topic]["one_hop_rels"] = dict()
        combined[topic]["two_hop_rels"] = dict()
        if (topic in questions):
            combined[topic]["question"] = questions[topic]
        else:
            no_topic = no_topic + 1
            # print("no question about: ", topic)
    print("no question for ", no_topic, " questions, out of the " + str(len(findItOut_concepts().keys())) + " concepts")

    concept_set = ("telephone directory", "side chair", "carpet", "floor")
    question_list = []
    for x in concept_set:
        if (x in combined.keys()):
            question_list.append(x)
            o_hop = []
            t_hop = []
            for z in combined[x]["one_hop"]:
                o_hop.append(z[0])
            for z in combined[x]["two_hop"]:
                t_hop.append(z[0])
            # print(o_hop[0:4], " ohop for: ", x)
            # print(t_hop[0:4], " thop for: ", x)

            res = o_hop.copy()
            res.extend(t_hop)

            res = list(set(res))
            # print(x, res[0:8])
            # print(x, o_hop[0:4], t_hop[0:4])

    # print(question_list)

    # print(combined["carpet"])

    o = open(config["paths"]["one_hop_with_relations"], encoding="utf8")

    for line in o.readlines():
        lt = line.split('\t')
        s = lt[0].strip()
        t = lt[2].strip()


        if(not (combined[s]["one_hop_rels"].keys().__contains__(t))):
            combined[s]["one_hop_rels"][t] = []
        relation = lt[0].strip() + " " + lt[1].strip() + " " + lt[2].strip()
        combined[s]["one_hop_rels"][t].append(relation)

    o.close()

    two_hop_file = open(config["paths"]["two_hop_with_relations"], encoding="utf8")

    for line in two_hop_file.readlines():
        lt = line.split('\t')
        s = lt[0].strip()
        t = lt[-1].strip()

        if (not (combined[s]["two_hop_rels"].keys().__contains__(t))):
            combined[s]["two_hop_rels"][t] = []
        relation = lt[0].strip() + " " + lt[1].strip() + " " + lt[2].strip() + " " +  lt[3].strip() + " " +  lt[4].strip()
        combined[s]["two_hop_rels"][t].append(relation)

    two_hop_file.close()

    return combined


if __name__ == "__main__":
    # example()
    rate_bert()
    #prepare_questions_topics()
