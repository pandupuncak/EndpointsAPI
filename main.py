
@app.get("/")
async def root():
    return "You are accessing root node, Hello."

#Get Menu based on ID
@app.get("/menu/{item_id}")
async def read_menu(item_id: int):

    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item

    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )

@app.get("/menu/")
async def get_all():

    return data['menu']

#Post Menu (Add New Menu Item)
@app.post("/menu/{item}")
async def add_menu(item : str):
    menu_item = {}
    item_id = data['menu'][len(data['menu']) - 1]["id"] + 1
    menu_item["id"] = item_id
    menu_item["name"] = item
    data['menu'].append(menu_item)

    #read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4, sort_keys=False)
        return menu_item

    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

#Update Menu Item
@app.put("/menu/")
async def update_item(item_id: int, item_name: str):
    found = False
    i = 0
    while (not found) and (i < len(data['menu'])):
        if(data['menu'][i]["id"] == item_id):
            found = True
        i = i + 1
    
    if found:
        data['menu'][item_id-1]["name"] = item_name
        with open("menu.json", "w") as write_file:
            json.dump(data, write_file, indent=4, sort_keys=False)
        return data['menu']

    # else:
    #     return "not found"
    
    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )

#Delete
@app.delete("/menu/")
async def delete_item(item_id: int):
    new_data = {}
    new_menu = []
    found = False
    for menu_item in data['menu']:
        if menu_item['id'] != item_id:
            new_menu.append(menu_item)
        else:
            found = True
    
    new_data["menu"] = new_menu
    if found:
        with open("menu.json", "w") as write_file:
            json.dump(new_data, write_file, indent=4, sort_keys=False)
        return new_menu
    
    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )