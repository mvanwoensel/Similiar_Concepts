import configparser
import json
import time
from transformers import AutoModel, AutoTokenizer
import torch
from scipy.spatial.distance import cosine


def compare_boards():
    config = configparser.ConfigParser()
    config.read("../conceptnet/paths.cfg")

    first_order = dict()
    second_order = dict()
    combined_order = dict()
    questions_mine = dict() #question -> concepts
    questions_findit = dict() #question -> concepts

    f = open(config["paths"]["generated_first_order"], encoding="utf8")
    for line in f.readlines():
        lt = line.split("|")
        concept = lt[0].strip()
        templist = []
        for con in lt[1:]:
            templist.append(con.strip())


        if(len(templist) > 0):
            first_order[concept] = templist

    f.close()
    print(len(first_order.keys()))

    f = open(config["paths"]["generated_second_order"], encoding="utf8")
    for line in f.readlines():
        lt = line.split("|")
        concept = lt[0].strip()
        templist = []
        for con in lt[1:]:
            templist.append(con.strip())

        if (len(templist) > 0):
            second_order[concept] = templist
    print(len(second_order.keys()))
    f.close()

    f = open(config["paths"]["generated_board"], encoding="utf8")
    for line in f.readlines():
        lt = line.split("\t")
        concept = lt[0].strip()
        question = lt[1].strip()
        print("question_mine", question, concept)
        questions_mine[question] = concept
        concepts = lt[2].split("|")[1:]
        templist = []
        for con in concepts:
            templist.append(con.strip())


        combined_order[concept] = templist
    f.close()

    # f = open(config["paths"]["generated_board"], encoding="utf8")
    # for line in f.readlines():
    #     lt = line.split("\t")
    #     concept = lt[0].strip()
    #     question = lt[1].strip()
    #     questions_mine[concept] = question
    #     concepts = lt[2].split("|")[1:]
    #     templist = []
    #     for con in concepts:
    #         templist.append(con.strip())
    #
    #     if (len(templist) > 0):
    #         combined_order[question] = templist
    print("combined len: ", len(combined_order.keys()))
    # f.close()



    f = open(config["paths"]["finditout_board"], encoding="utf8")
    for line in f.readlines():
        lt = line.split("|")
        questions = lt[0].split("\t")[0:-1]

        questions_mine[concept] = question
        concepts = lt[1:]
        templist = []
        for con in concepts:
            templist.append(con.strip())


        for que in questions:
            if(questions_findit.__contains__(que)):
                print("duplicate for: " , que)
            questions_findit[que] = templist
    f.close()

    inbothsets = set(questions_findit.keys()).intersection(questions_mine.keys())
    print("in both sets:", len(inbothsets))


    scores = dict()


    for question in inbothsets:
        tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-bert-base-uncased")
        model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-bert-base-uncased")

        text = [question]

        print("question ", question)
        print("my concept ", questions_mine[question])
        findit_concepts = questions_findit[question]
        my_concepts = combined_order[questions_mine[question]]
        text.extend(my_concepts)
        text.extend(findit_concepts)

        if(len(my_concepts) == 0):
            print("no concepts for: ", question)
            continue
        if(len(findit_concepts) == 0):
            continue



        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

        with torch.no_grad():
            embeddings = model(**inputs, output_hidden_states=True, return_dict=True).pooler_output

        cosine_sims = []
        for i in range(len(text)):
            if not (i == 0):
                cosine_sims.append((text[i], 1 - cosine(embeddings[0], embeddings[i])))


        cutoff = len(my_concepts)

        results_mine = cosine_sims[0:cutoff]
        results_findit = cosine_sims[cutoff:]

        results_mine.sort(key=lambda x: x[1], reverse=True)
        results_findit.sort(key=lambda x: x[1], reverse=True)

        # print("question:" , question)

        # print("my concepts: ",my_concepts)
        # print("my resulsts:", results_mine)
        # print("findit concepts: ", findit_concepts)
        # print("results findit: ", results_findit)

        total_mine = 0
        for x in results_mine:
            total_mine = total_mine + x[1]
        avg_mine = total_mine / len(results_mine)

        total_findit = 0
        for x in results_findit:
            total_findit = total_findit + x[1]
        avg_findit = total_findit / len(results_findit)

        print(question)
        print("best mine:", results_mine[0])
        print("avg_mine", avg_mine)

        print("best findit: ", results_findit[0])
        print("avg_findit", avg_findit )
        #print(results_findit)


        scores[question] = dict()
        scores[question]["best_mine"] = results_mine[0]
        scores[question]["best_findit"] = results_findit[0]
        scores[question]["avg_mine"] = avg_mine
        scores[question]["avg_findit"] = avg_findit
        scores[question]["findit"] = results_findit
        scores[question]["mine"] = results_mine

    list_best_mine = []
    list_avg_mine = []
    list_best_findit = []
    list_avg_findit = []


    w = open(config["paths"]["score"], "w", encoding="utf8")
    w.write("question best_mine, avg_mine, best_findit, avg_findit \n")
    for que in scores.keys():
        line = str(scores[que]["best_mine"][1]) +"\t" + str(scores[que]["avg_mine"]) +"\t" + str(scores[que]["best_findit"][1]) +"\t" +  str(scores[que]["avg_findit"])
        list_best_mine.append(scores[que]["best_mine"][1])
        list_avg_mine.append(scores[que]["avg_mine"])
        list_best_findit.append(scores[que]["best_findit"][1])
        list_avg_findit.append(scores[que]["avg_findit"])
        w.write(line + "\n")


    z = open(config["paths"]["score_dumb"], "w", encoding="utf8")
    z.write("best_mine \n")
    for x in list_best_mine:
       z.write(str(x) + "\n")

    z.write("avg_mine \n")
    for x in list_avg_mine:
        z.write(str(x) + "\n")

    z.write("best_findit \n")
    for x in list_best_findit:
        z.write(str(x) + "\n")

    z.write("avg_findit \n")
    for x in list_avg_findit:
        z.write(str(x) + "\n")


if __name__ == '__main__':
    compare_boards()