import configparser
import json
import time

relation_mapping = dict()


def load_merge_relation():
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    with open(config["paths"]["merge_relation"], encoding="utf8") as f:
        for line in f.readlines():
            ls = line.strip().split('/')
            rel = ls[0]
            for l in ls:
                if l.startswith("*"):
                    relation_mapping[l[1:]] = "*" + rel
                else:
                    relation_mapping[l] = rel


def del_pos(s):
    """
    Deletes part-of-speech encoding from an entity string, if present.
    :param s: Entity string.
    :return: Entity string with part-of-speech encoding removed.
    """
    if s.endswith("/n") or s.endswith("/a") or s.endswith("/v") or s.endswith("/r"):
        s = s[:-2]
    return s


def extract_english():
    """
    Reads original conceptnet csv file and extracts all English relations (head and tail are both English entities) into
    a new file, with the following format for each line: <relation> <head> <tail> <weight>.
    :return:
    """
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    only_english = []
    with open(config["paths"]["conceptnet"], encoding="utf8") as f:
        for line in f.readlines():
            ls = line.split('\t')
            if ls[2].startswith('/c/en/') and ls[3].startswith('/c/en/'):
                """
                Some preprocessing:
                    - Remove part-of-speech encoding.
                    - Split("/")[-1] to trim the "/c/en/" and just get the entity name, convert all to 
                    - Lowercase for uniformity.
                """
                rel = ls[1].split("/")[-1].lower()
                head = del_pos(ls[2]).split("/")[-1].lower()
                tail = del_pos(ls[3]).split("/")[-1].lower()

                if not head.replace("_", "").replace("-", "").isalpha():
                    continue

                if not tail.replace("_", "").replace("-", "").isalpha():
                    continue

                if rel not in relation_mapping:
                    continue
                rel = relation_mapping[rel]
                if rel.startswith("*"):
                    rel = rel[1:]
                    tmp = head
                    head = tail
                    tail = tmp

                data = json.loads(ls[4])

                only_english.append("\t".join([rel, head, tail, str(data["weight"])]))

    with open(config["paths"]["conceptnet_en"], "w", encoding="utf8") as f:
        f.write("\n".join(only_english))


def extract_english_head_relation_tail():
    """
    Reads original conceptnet csv file and extracts all English relations (head and tail are both English entities) into
    a new file, with the following format for each line: <relation> <head> <tail> <weight>.
    :return:
    """
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    filtered = False
    allowed_concepts = {}
    if (filtered):
        allowed_concepts = findItOut_concepts()

    only_english = []
    with open(config["paths"]["conceptnet"], encoding="utf8") as f:
        lines = f.readlines()

        counter = 0
        max = len(lines)
        time_start = time.time()
        prev_percent = 0

        for line in lines:
            ls = line.split('\t')
            if ls[2].startswith('/c/en/') and ls[3].startswith('/c/en/'):
                """
                Some preprocessing:
                    - Remove part-of-speech encoding.
                    - Split("/")[-1] to trim the "/c/en/" and just get the entity name, convert all to 
                    - Lowercase for uniformity.
                """
                percent = round(((counter / max) * 1000))
                if percent != prev_percent:
                    prev_percent = percent
                    print("task at " + str(percent) + "%")
                    time_current = time.time()
                    time_since_start = round(time_current - time_start);
                    print(str(time_since_start) + " seconds since starting task")
                counter = counter + 1

                #print(counter)


                rel = ls[1].split("/")[-1].lower()
                head = del_pos(ls[2]).split("/")[-1].lower()
                tail = del_pos(ls[3]).split("/")[-1].lower()

                if not head.replace("_", "").replace("-", "").isalpha():
                    continue

                if not tail.replace("_", "").replace("-", "").isalpha():
                    continue

                if rel not in relation_mapping:
                    continue

                rel = relation_mapping[rel]
                if rel.startswith("*"):
                    rel = rel[1:]
                    tmp = head
                    head = tail
                    tail = tmp

                if (head == tail):
                    continue

                data = json.loads(ls[4])

                sentence = "\t".join([head, rel, tail, str(data["weight"])])

                #if (only_english.__contains__(sentence)):
                #    continue

                if (filtered):
                    if (allowed_concepts.__contains__(head) and allowed_concepts.__contains__(tail)):
                        only_english.append(sentence)
                else:
                    only_english.append(sentence)



    file = config["paths"]["head_relation_tail"]
    if (filtered):
        file = config["paths"]["head_relation_tail_filtered"]

    with open(file, "w", encoding="utf8") as f:
        f.write("\n".join(only_english))


def sort_by_concept():
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    ordered = []
    with open(config["paths"]["head_relation_tail"], encoding="utf8") as f:
        lines = f.readlines()
        lines.sort()
        for line in lines:
            lt = line.split('\t')
            h = lt[0]
            r = lt[1]
            t = lt[2]
            w = float(lt[3].strip())
            newline = (h, r, t, w)
            # no duplicates and no self refrences
            if(len(ordered) > 0):
                if(ordered[-1] != newline and h != t):
                    ordered.append(newline)
            else:
                ordered.append(newline)

    with open(config["paths"]["sorted"], "w", encoding="utf8") as g:
        for h, r, t, w in ordered:
            g.write("%s\t%s\t%s\t%f\n" % (h, r, t, w))


# returns a set with all the concepts that were used in the FindItOut game.
def findItOut_concepts():
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    concepts = {}
    with open(config["paths"]["find_it_out_concepts"], encoding="utf8") as f:
        lines = f.readlines()

        for line in lines:
            lt = line.split('\t')
            concepts[lt[0]] = lt[0]




    return concepts


if __name__ == "__main__":
    #load_merge_relation()
    # print(relation_mapping)
    print("starting extracting")
    #extract_english_head_relation_tail()
    print("finished extracting")
    sort_by_concept()
    print("finished sorting")
