
def make_list():



    item_list = ["Doctor Strange", "Slime", "Cats", "Nike", "Animal Crossing", "Jewelry", "Hats"]

    c_list=[]

    while len(item_list) > 1:
        for i in range(1, len(item_list)):
            new_item = item_list[0] + " " + item_list[i]
            c_list.append(new_item)

        item_list.remove(item_list[0])

    print c_list
    return c_list
