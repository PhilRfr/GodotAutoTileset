func load_tileset():
	var root_node = Node2D.new()
	var file = File.new()
	file.open("res://result.json", file.READ)
	var text = file.get_as_text()
	file.close()
	var dict = JSON.parse(text).result
	var texture = load("res://tileset.png")
	var tiles = dict["tiles"]
	root_node.name = "tileset"
	var l = tiles.keys()
	var x = 5
	var m = []
	for i in range(x):
		m.append(l[i])
	l = {}
	for k in m:
		l[k] = tiles[k]
	for key in tiles:
		var sprite = Sprite.new()
		sprite.name = "tile_"+str(key)
		var tile = tiles[key]
		sprite.region_enabled = true
		sprite.texture = texture
		sprite.centered = false
		var rect = tile['clip']
		sprite.region_rect = Rect2(rect[0],rect[1],rect[2],rect[3])
		sprite.position = Vector2(tile['position'][0], tile['position'][1])
		root_node.add_child(sprite)
		if(tile['collision'] != null):
			var collisionPolygon = CollisionPolygon2D.new()
			var staticBody = StaticBody2D.new()
			var collisionArray = []
			for pt in tile['collision']:
				collisionArray.append(Vector2(pt['x'], pt['y']))
			collisionPolygon.polygon = PoolVector2Array(collisionArray)
			collisionPolygon.name = "tile_"+str(key) + "_collision_polygon"
			staticBody.name = "tile_"+str(key) + "_staticbody"
			staticBody.add_child(collisionPolygon)
			sprite.add_child(staticBody)
			collisionPolygon.owner = root_node
			staticBody.owner = root_node
		if(tile['navigation'] != null):
			var navigationNode = NavigationPolygonInstance.new()
			var navigationPolygon = NavigationPolygon.new()
			var navigationArray = []
			for pt in tile['navigation']:
				navigationArray.append(Vector2(pt['x'], pt['y']))
			navigationNode.name = "tile_" + str(key) + "_navigation"
			navigationPolygon.add_outline(navigationArray)
			navigationPolygon.make_polygons_from_outlines()
			navigationNode.navpoly = navigationPolygon
			sprite.add_child(navigationNode)
			navigationNode.owner = root_node
		sprite.owner = root_node
	var packed_scene = PackedScene.new()
	packed_scene.pack(root_node)
	ResourceSaver.save("res://my_scene.tscn", packed_scene)
