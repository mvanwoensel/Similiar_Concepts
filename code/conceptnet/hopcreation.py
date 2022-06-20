# creates the csv files for 1 hop neighbours and uses that aswell for 2nd hop neighbours
import configparser
import json
from extract_cpnet import findItOut_concepts
import time


def create_one_hop():
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    dic = dict()

    with open(config["paths"]["sorted"], encoding="utf8") as f:
        for line in f.readlines():
            lt = line.split('\t')
            head = lt[0]
            rel = lt[1]
            tail = lt[2]
            w = lt[3]
            if(head == tail):
                break

            if (not dic.__contains__(head)):
                dic[head] = dict()


            s = dic[head]
            if(not s.__contains__(rel)):
                s[rel] = set()
            s[rel].add(tail)

            if ( not dic.__contains__(tail)):
                dic[tail] = dict()

            rel = 'fake'
            t = dic[tail]
            if(not t.__contains__(rel)):
                t[rel] = set()
            t[rel].add(tail)

            #print(relations[head][tail])


    # finditout concepts
    findit = findItOut_concepts()


    create_two_hopv2(dic,findit)



def create_one_hop_v2():
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    dic = dict()

    lines = []

    with open(config["paths"]["sorted"], encoding="utf8") as f:
        finditoutconcepts = findItOut_concepts()
        readlines = f.readlines()
        for line in readlines:
            lt = line.split('\t')
            head = lt[0]
            rel = lt[1]
            tail = lt[2]
            w = lt[3]

            if (not (head == tail) ) and finditoutconcepts.__contains__(head) and finditoutconcepts.__contains__(tail):
                lines.append(head + "\t" + rel + "\t" + tail)




            # print(relations[head][tail])

    lines.sort()

    with open(config["paths"]["one_hop_with_relations"], "w", encoding="utf8") as w:
        for x in lines:
            w.write(x + "\n")

def create_two_hopv2(dic, findit):
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    #dic = dict()
    count = 0;
    total_relations = []
    for s in findit: # start concept
        n1 = dic[s]  # dictonary[relations]
        for rel in n1.keys(): #for each of these relations
            for x in n1[rel]: # for each neighbour check if there is overlap with the findit set
                neigborset = dic[x]
                #n2 = n1[x].values().intersection(findit) #check all neighbours
                relations = dic[x].keys()
                for rel2 in relations:
                    n2 = dic[x][rel2].intersection(findit)
                    if len(n2) >0:
                        for t in n2:
                            if not((s == x) or (s == t) or (t == x)):
                                new_relation = s +"\t"+ rel +"\t"+ x +"\t"+ rel2 +"\t" + t
                                total_relations.append(new_relation)


    print(len(total_relations))
    total_relations.sort()
    with open(config["paths"]["two_hop_with_relations"], "w", encoding="utf8") as g:
        for x in total_relations:
            g.write(x + "\n")



    # rel = []
    # for x in one_hop:
    #     connections = len(one_hop[x])
    #     rel.append(connections)
    #     if (connections == 727):
    #         print(x)
    # rel.sort(reverse=True)
    #
    #write_to_file(one_hop, config["paths"]["one_hop"])

    #create_two_hop(dic,findit)

def create_two_hop(dic, findit):
    dic2 = {}

    counter = 0
    max = len(dic.keys())
    time_start = time.time()
    prev_percent = 0

    for key in dic.keys():
        order_two = set()
        # print(type(dic[key]))
        for key2 in dic[key]:
            s2 = dic[key2]
            s3 = order_two.union(s2)
            order_two = s3
            # print(type(dic[key2]))
            # print(len(dic[key2]))
        dic2[key] = order_two
        # print(order_two)

        percent = round(((counter / max) * 100))
        if percent != prev_percent:
            prev_percent = percent
            print("task at " + str(percent) + "%")
            time_current = time.time()
            time_since_start = round(time_current - time_start);
            print(str(time_since_start) + " seconds since starting task")
        counter = counter + 1

    does_not_contain2 = []

    print(len(dic2))

    counter = 0
    max = len(findit) * len(findit)
    time_start = time.time()
    prev_percent = 0

    two_hop = {}
    for key in findit:
        two_hop[key] = {}
        for key2 in findit:
            if ((key != key2)):
                # if (dic2.__contains__(key)):
                #     if (dic2.__contains__(key2)):
                s1 = dic2[key]
                s2 = dic2[key2]
                inter = len(s1.intersection(s2))
                # print(inter)
                # print(key2)

                if percent != prev_percent:
                    prev_percent = percent
                    print("task at " + str(percent) + "%")
                    time_current = time.time()
                    time_since_start = round(time_current - time_start);
                    print(str(time_since_start) + " seconds since starting task")
                counter = counter + 1

                if (inter > 0):
                    s3 = s1.union(s2)
                    two_hop[key][key2] = str(inter) + "\t" + str(len(s3))
            #     else:
            #         if (not does_not_contain2.__contains__(key2)):
            #             does_not_contain.append(key2)
            # else:
            #     if (not does_not_contain2.__contains__(key)):
            #         does_not_contain.append(key)

    # rel = []
    # for x in two_hop:
    #     connections = len(two_hop[x])
    #     rel.append(connections)
    #     # if (connections == 727):
    #     #     print(x)
    # rel.sort(reverse=True)

    config = configparser.ConfigParser()
    config.read("paths.cfg")

    write_to_file(two_hop, config["paths"]["two_hop"])


def write_to_file(dic, file):
    with open(file, "w", encoding="utf8") as g:
        for key in dic.keys():
            # g.write(key + "\t" +  str(dic[key]) + "\n")
            for key2 in dic[key]:
                line = key + "\t" + key2 + "\t"
                val = dic[key][key2]
                line = line + val + "\n"
                g.write(line)




def read_hop(file):
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    dict = {}
    concepts = findItOut_concepts()
    for x in concepts:
        dict[x] = []

    with open(config["paths"][file], encoding="utf8") as g:
        for line in g.readlines():
            lt = line.split('\t')
            head = lt[0]
            tail = lt[1]
            w1 = lt[2]
            w2 = lt[3]

            dict[head].append((str(tail), int(w1), int(w2)))

    for x in concepts:
        dict[x].sort(key= lambda x: x[1], reverse=True)

    return dict

def create_first_order():
    config = configparser.ConfigParser()
    config.read("paths.cfg")

    f = open(config["paths"]["sorted"], encoding="utf8")

    dic = dict()

    findit = findItOut_concepts()

    for line in f.readlines():
        lt = line.split("\t")
        head = lt[0].strip()
        rel = lt[1].strip()
        tail = lt[2].strip()
        w = lt[3].strip()

        if(not dic.keys().__contains__(head)):
            dic[head] = set()

        dic[head].add(tail)

    concepts_sorted = list(dic.keys())
    concepts_sorted.sort()

    w = open(config["paths"]["first_order"], "w", encoding="utf8")
    print(concepts_sorted.__contains__("fairgrounds"))

    to_remove = []
    for x in findit:
        if not concepts_sorted.__contains__(x):
            to_remove.append(x)

    for x in to_remove:
        del findit[x]
        print("removed " ,x)

    first_order_terms = set()

    first_order_terms = first_order_terms.union(findit)

    for x in findit:
        for z in findit:
            set_x = dic[x]
            first_order_terms = first_order_terms.union(set_x)
            if(not (x == z)):
                set_z = dic[z]
                overlap = set_x.intersection(set_z)
                union = set_x.union(set_z)
                if(len(overlap) > 0):
                    w.write(x + "\t" + z + "\t" + str(len(overlap)) + "\t" + str(len(union)) + "\n")


    second_order = dict()
    print(len(first_order_terms))
    for x in first_order_terms:
        if(dic.keys().__contains__(x)):
            temp_set = set()
            for con in dic[x]:
                if (dic.keys().__contains__(con)):
                    #print(findit.__contains__(con))
                    temp_set = temp_set.union(dic[con])
            second_order[x] = temp_set



    write_file = open(config["paths"]["second_order"], "w", encoding="utf8")

    missed = set()

    for x in findit:
        for z in first_order_terms:
            set_x = second_order[x]
            if (not (x == z)):
                if second_order.keys().__contains__(z):
                    set_z = second_order[z]
                    overlap = set_x.intersection(set_z)
                    union = set_x.union(set_z)
                    if(len(overlap) > 0):
                        write_file.write(x + "\t" + z + "\t" + str(len(overlap)) + "\t" +  str(len(union)) + "\n")
                else:
                    missed.add(z)

    print(len(missed))



if __name__ == "__main__":
    startt = time.time();
    #create_one_hop()
    #create_one_hop_v2()

    create_first_order()

    fint = time.time();
    runt = fint-startt

    print("took {} seconds", runt )

    # read_attempt()
