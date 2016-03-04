import cv2
import time
import numpy as np
from os import listdir
from itertools import product
from os.path import isfile, join, split

def saliecny_score(integ_sal_map, x, y, w, h, width, height, maxDiff=False):
	if maxDiff == True:
		avg_sal = (integ_sal_map[y][x] + integ_sal_map[y+h][x+w] - integ_sal_map[y+h][x] - integ_sal_map[y][x+w]) / float(w * h)
		outer_avg_sal = (integ_sal_map[height][width] - integ_sal_map[y][x] - integ_sal_map[y+h][x+w] +
			integ_sal_map[y+h][x] + integ_sal_map[y][x+w]) / float(width * height - w * h)
		score = avg_sal - outer_avg_sal
	else:
		score = (integ_sal_map[y][x] + integ_sal_map[y+h][x+w] - integ_sal_map[y+h][x] - integ_sal_map[y][x+w]) / float(w * h)
	return score

def saliency_crop(imgPath, salPath, maxDiff=False):
	start_time = time.time()

	img = cv2.imread(imgPath)
	sal_map = cv2.imread(salPath, cv2.IMREAD_GRAYSCALE)
	integ_sal_map = cv2.integral(sal_map)	# integral image for fast block sum computation
	#print integ_sal_map.shape

	# clone of the original image and saliency map for visualizing results
	map_canvas = np.copy(sal_map)
	img_canvas = np.copy(img)

	height = img.shape[0]
	width = img.shape[1]

	best_x = -1
	best_y = -1
	best_w = -1
	best_h = -1
	best_score = -1.0

	# uniform scaling
	scales = [0.5, 0.6, 0.7, 0.8, 0.9]
	for scale in scales:
		w = int(width * scale)
		h = int(height * scale)
		#print w, h

		# generate the grid vertices of sliding windows
		X = [x for x in range(0, width, int(round((width-w)/5.0))) if x < width - w]
		Y = [y for y in range(0, height, int(round((height-h)/5.0))) if y < height - h]
		#X = [x for x in range(0, width, 5) if x < width - w]
		#Y = [y for y in range(0, height, 5) if y < height - h]

		for x, y in product(X, Y):
			if maxDiff == True:		# maximum saliency difference betwen the cropped window and the rest region
				avg_sal = (integ_sal_map[y][x] + integ_sal_map[y+h][x+w] - integ_sal_map[y+h][x] - integ_sal_map[y][x+w]) / float(w * h)
				outer_avg_sal = (integ_sal_map[height][width] - integ_sal_map[y][x] - integ_sal_map[y+h][x+w] +
					integ_sal_map[y+h][x] + integ_sal_map[y][x+w]) / float(width * height - w * h)
				score = avg_sal - outer_avg_sal
			else:	# average saliency
				#score = np.sum(sal_map[y:y+h, x:x+w]) / float(w * h)
				#print 'sum:', score
				score = (integ_sal_map[y][x] + integ_sal_map[y+h][x+w] - integ_sal_map[y+h][x] - integ_sal_map[y][x+w]) / float(w * h)
				#print 'int:', score

			if score > best_score:
				best_x = x
				best_y = y
				best_w = w
				best_h = h
				best_score = score

	#print best_x, best_y, best_w, best_h, best_score
	#print "computation time: %s seconds" % (time.time() - start_time)

	#cv2.rectangle(img_canvas, (best_x, best_y), (best_x+best_w, best_y+best_h), (0,0,255), 2)
	#cv2.rectangle(map_canvas, (best_x, best_y), (best_x+best_w, best_y+best_h), (0,0,255), 2)

	#cv2.imshow('Image', img_canvas)
	#cv2.imshow('Saliency', map_canvas)
	#key = cv2.waitKey(0)

	#cv2.destroyAllWindows()
	return (best_x, best_y, best_w, best_h)

def overlap_ratio(x1, y1, w1, h1, x2, y2, w2, h2):
	intersection = max(0, min(x1+w1, x2+w2) - max(x1, x2)) * max(0, min(y1+h1, y2+h2) - max(y1, y2))
	union = (w1 * h1) + (w2 * h2) - intersection
	return float(intersection) / float(union)

def main():
	#print overlap_ratio(1, 1, 10, 10, 2, 2, 10, 10)
	#saliency_crop('source/101.jpg', 'map/101.jpg', True)

	source_img_root = '../data/'
	saliency_map_root = '../BMS/'
	maxDiff = True
	'''
	filelist = '../split/crop/test_0.1.txt'
	with open(filelist, 'r') as f:
		data = f.readlines()

	cnt = 0
	accum_boundary_displacement = 0
	accum_overlap_ratio = 0
	for i in xrange(len(data)):
		meta = data[i].split(' ')
		filename = split(meta[1])[-1]
		x = int(meta[2])
		y = int(meta[3])
		w = int(meta[4])
		h = int(meta[5])

		if isfile(join(saliency_map_root, filename.replace('jpg','png'))):
			best_x, best_y, best_w, best_h = saliency_crop(join(source_img_root, filename), join(saliency_map_root, filename.replace('jpg','png')), maxDiff)
			boundary_displacement = abs(best_x - x) + abs(best_y - y) + abs(best_x + best_w - x - w) + abs(best_y + best_h - y - h)
			accum_boundary_displacement += boundary_displacement
			ratio = overlap_ratio(x, y, w, h, best_x, best_y, best_w, best_h)
			accum_overlap_ratio += ratio
			cnt += 1

	print 'Average boundary displacement:', accum_boundary_displacement / (cnt * 4.0)
	print 'Average overlap ratio:', accum_overlap_ratio / cnt
	'''

	filelist = '../split/rank/test_1.txt'
	with open(filelist, 'r') as f:
		data = f.readlines()

	cnt = 0
	total = 0
	for i in xrange(len(data)):
		meta = data[i].split(' ')
		filename = split(meta[1])[-1]
		x0 = int(meta[2])
		y0 = int(meta[3])
		w0 = int(meta[4])
		h0 = int(meta[5])
		x1 = int(meta[6])
		y1 = int(meta[7])
		w1 = int(meta[8])
		h1 = int(meta[9])
		vote_crop_0 = int(meta[10])

		saliency_filename = join(saliency_map_root, filename.replace('jpg','png'))
		if isfile(saliency_filename):
			sal_map = cv2.imread(saliency_filename, cv2.IMREAD_GRAYSCALE)
			integ_sal_map = cv2.integral(sal_map)
			height = sal_map.shape[0]
			width = sal_map.shape[1]
			score_0 = saliecny_score(integ_sal_map, x0, y0, w0, h0, width, height, maxDiff)
			score_1 = saliecny_score(integ_sal_map, x1, y1, w1, h1, width, height, maxDiff)
			if vote_crop_0 >= 3 and score_0 > score_1:
				cnt += 1
			elif vote_crop_0 < 3 and score_0 < score_1:
				cnt += 1
			total += 1

	print 'Ranking accuracy (%d/%d): %f' % (cnt, total, float(cnt) / float(total))


if __name__ == "__main__":
	main()
