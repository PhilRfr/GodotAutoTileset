import argparse
import json
import math
import matplotlib.pyplot as plt
import numpy
from shapely import geometry
import PIL
from PIL import ImageOps
import skimage

parser = argparse.ArgumentParser(description='Split a tileset into pieces.')
parser.add_argument('filename', type=str,help='Source image file')
parser.add_argument('tile_width', type=int,help='Tile width')
parser.add_argument('tile_height', type=int,help='Tile height')
parser.add_argument('tile_spacing_horizontal', type=int,help='Tile spacing horizontal')
parser.add_argument('tile_spacing_vertical', type=int,help='Tile spacing vertical')

args = parser.parse_args()

cell_width = args.tile_width + args.tile_spacing_horizontal
cell_height = args.tile_height + args.tile_spacing_vertical

def as_vector2(pt):
	return "Vector2({0},{1})".format(pt[1],pt[0])

def as_poolvector2array(contour):
	PoolVector2Array = []
	for pt in contour:
		PoolVector2Array.append(as_vector2(pt))
	return "PoolVector2Array([{0}])".format(','.join(PoolVector2Array))

def as_list(contour, image):
	if(contour is None):
		return contour
	poly = simplify(contour, image)
	PoolVector2Array = []
	for pt in poly:
		PoolVector2Array.append({'x':pt[1],'y':pt[0]})
	return PoolVector2Array

def as_listnofix(poly):
	PoolVector2Array = []
	for pt in poly:
		PoolVector2Array.append({'x':pt[0],'y':pt[1]})
	return PoolVector2Array

def simplify(contour, image):
	tile_width, tile_height = image.size
	polygon = geometry.Polygon([[p[0]-1, p[1]-1] for p in contour])
	box = geometry.box(0,0,tile_width, tile_height)
	polygon = polygon.intersection(box)
	cleaned = polygon.simplify(0.5)
	x, y = cleaned.exterior.coords.xy
	shape = []
	for pt in zip(x,y):
		shape.append(pt)
	return shape


def determine_contours(image):
	contour = None
	image_layer = skimage.color.rgb2gray(numpy.array(image)) # Convert to numpy array for skimage
	contours = skimage.measure.find_contours(image_layer, 0.8)
	if(len(contours) > 0):
		contour = contours[0]
	return contour

def count_nonblack_pil(img):
    """Return the number of pixels in img that are not black.
    img must be a PIL.Image object in mode RGB.

    """
    bbox = img.getbbox()
    if not bbox: return 0
    return sum(img.crop(bbox)
               .point(lambda x: 255 if x else 0)
               .convert("L")
               .point(bool)
               .getdata())

def analyze_tile(tile):
	collision = None
	navigation = None
	dimensions = tile.size
	new_dimensions = dimensions[0]+2, dimensions[1]+2
	tile_alpha = PIL.Image.frombytes("L", tile.size, tile.tobytes("raw", "A"))
	white = count_nonblack_pil(tile_alpha)
	if white == 0:
		#tile is passing
		navigation = as_listnofix([(0,0),(0,dimensions[1]),(dimensions[0],dimensions[1]),(dimensions[0],0)])
	elif white == dimensions[0]*dimensions[1]:
		#tile is blocking
		collision = as_listnofix([(0,0),(0,dimensions[1]),(dimensions[0],dimensions[1]),(dimensions[0],0)])
	else:
		#tricky case
		bordered_tile = PIL.Image.new('L', new_dimensions)
		bordered_tile.paste( 0, [0,0,new_dimensions[0],new_dimensions[1]])
		bordered_tile.paste(tile_alpha, [1,1] )
		inverted_bordered_tile = PIL.Image.new('L', new_dimensions)
		inverted_bordered_tile.paste( 0, [0,0,new_dimensions[0],new_dimensions[1]])
		inverted_bordered_tile.paste(ImageOps.invert(tile_alpha), [1,1] )
		collision = as_list(determine_contours(bordered_tile), tile)
		navigation = as_list(determine_contours(inverted_bordered_tile), tile)
	return {'collision' : collision, 'navigation' : navigation}

image = PIL.Image.open(args.filename)
w,h = image.size
tiles_vertical = math.ceil(h/cell_height)
tiles_horizontal = math.ceil(w/cell_width)
tile_id = 0
tiles = {}
for y in range(tiles_vertical):
	for x in range(tiles_horizontal):
		left = x*cell_width
		top = y*cell_height
		position = [x*args.tile_width, y*args.tile_height]
		right = left + args.tile_width
		bottom = top + args.tile_height
		box = (left, top, right, bottom)
		clip = (left, top, args.tile_width, args.tile_height)
		area = image.crop(box)
		tile = analyze_tile(area)
		tile['id'] = tile_id
		tile['clip'] = clip
		tile['position'] = position
		tiles[tile_id] = tile
		tile_id += 1
fil = {'tiles':tiles}
json.dump(fil, open("result.json", 'w'), indent=4, sort_keys=True)