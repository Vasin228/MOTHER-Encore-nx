extends MainLoop

var _default_shader
var _default_texture
var _empty_stylebox := StyleBoxEmpty.new()

func _import_bbg(path: String):
	var file := ConfigFile.new()
	var node := PanelContainer.new()
	node.add_stylebox_override("panel", _empty_stylebox)
	node.name = "BBG"
	node.anchor_top = 0
	node.anchor_bottom = 1
	node.anchor_left = 0
	node.anchor_right = 1

	if file.load(path) != OK:
		return null

	var layer_sections: PoolStringArray = file.get_sections()
	layer_sections.remove(0)

	var shader_path_prefix = file.get_value("", "shader_folder", "res://")

	for layer_section in layer_sections:
		var keys: Array = file.get_section_keys(layer_section)
		if not "shader" in keys:
			push_error("Layer %s doesn't contain a shader." % layer_section)
			continue

		var shader_entry = str(file.get_value(layer_section, "shader", "[DEFAULT]"))
		var shader_path := ""
		var shader: Shader
		if shader_entry == "[DEFAULT]":
			shader = _default_shader
		else:
			shader_path = (shader_path_prefix + "/" + shader_entry).simplify_path()
			shader = load(shader_path)
		keys.erase("shader")
		if not shader:
			push_error("Error loading shader at %s." % shader_path)
			continue

		var material := ShaderMaterial.new()
		material.shader = shader

		var layer_node := TextureRect.new()
		layer_node.stretch_mode = TextureRect.STRETCH_SCALE
		layer_node.material = material
		layer_node.name = layer_section
		var backbuffer := BackBufferCopy.new()
		backbuffer.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
		layer_node.add_child(backbuffer)
		node.add_child(layer_node, true)
		layer_node.owner = node
		backbuffer.owner = node

		if "texture" in keys:
			var texture_entry = str(file.get_value(layer_section, "texture", "res://icon.png"))
			var texture_path := ""
			var new_texture: Texture
			if texture_entry == "[DEFAULT]":
				new_texture = _default_texture
			else:
				texture_path = (shader_path_prefix + "/" + texture_entry).simplify_path()
				keys.erase("texture")
				new_texture = load(texture_path)
			if new_texture:
				layer_node.texture = new_texture
			else:
				push_error("Error loading texture at %s." % texture_path)

		if "texture_stretch" in keys:
			var stretch_modes = ["STRETCH_SCALE_ON_EXPAND", "STRETCH_SCALE", "STRETCH_TILE", "STRETCH_KEEP"]
			keys.erase("texture_stretch")
			var texture_stretch: String = file.get_value(layer_section, "texture_stretch", "STRETCH_SCALE")
			layer_node.stretch_mode = stretch_modes.find(texture_stretch)

		for key in keys:
			var uniform_value = file.get_value(layer_section, key, null)
			if key == "blending":
				uniform_value = int(uniform_value)
			if uniform_value is String and uniform_value.begins_with("[Resource]"):
				uniform_value = load(("res://" + uniform_value.trim_prefix("[Resource]")).simplify_path())
			material.set_shader_param(key, uniform_value)

	return node

func _initialize():
	_default_shader = load("res://addons/distortionator_integration/default_shader.tres")
	_default_texture = load("res://addons/distortionator_integration/background.png")
	var dir := Directory.new()
	var bgs_dir := "res://Graphics/Battle BGS"
	if dir.open(bgs_dir) != OK:
		push_error("Cannot open " + bgs_dir)
		OS.exit_code = 1
		return
	dir.list_dir_begin(true, true)
	var ok_count := 0
	var fail_count := 0
	while true:
		var fn := dir.get_next()
		if fn == "":
			break
		if not fn.ends_with(".bbg.import"):
			continue
		var cfg := ConfigFile.new()
		var imp_path := bgs_dir + "/" + fn
		if cfg.load(imp_path) != OK:
			push_error("Failed to load " + imp_path)
			fail_count += 1
			continue
		var src_path: String = cfg.get_value("deps", "source_file", "")
		var dest_path: String = cfg.get_value("remap", "path", "")
		var node = _import_bbg(src_path)
		if node == null:
			push_error("Importer returned null for " + src_path)
			fail_count += 1
			continue
		var packed := PackedScene.new()
		var perr := packed.pack(node)
		node.free()
		if perr != OK:
			push_error("pack() failed (%d) for %s" % [perr, src_path])
			fail_count += 1
			continue
		var serr := ResourceSaver.save(dest_path, packed)
		if serr != OK:
			push_error("save() failed (%d) for %s" % [serr, dest_path])
			fail_count += 1
			continue
		ok_count += 1
	dir.list_dir_end()
	print("BBG_IMPORT_DONE ok=%d fail=%d" % [ok_count, fail_count])
	var test_res = load("res://Graphics/Battle BGS/antoid.bbg")
	if test_res is PackedScene:
		var inst = test_res.instance()
		print("BBG_SMOKE_TEST OK: class=%s children=%d" % [inst.get_class(), inst.get_child_count()])
		inst.free()
	else:
		push_error("BBG_SMOKE_TEST FAILED")
		fail_count += 1
	OS.exit_code = 0 if (fail_count == 0 and ok_count == 50) else 1

func _iteration(_delta):
	return true

func _idle(_delta):
	return true
