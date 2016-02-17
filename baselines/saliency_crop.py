import cv2
import time
import numpy as np
from os import listdir
from itertools import product
from os.path import isfile, join

def saliency_crop(imgPath, salPath, maxDiff=False):
	start_time = time.time()

	img = cv2.imread(imgPath)
	sal_map = cv2.imread(salPath, cv2.IMREAD_GRAYSCALE)
	integ_sal_map = cv2.integral(sal_map)
	#print sal_map.shape

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
		X = [x for x in range(0, width, 5) if x < width - w]
		Y = [y for y in range(0, height, 5) if y < height - h]

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

	print best_x, best_y, best_w, best_h, best_score
	print "computation time: %s seconds" % (time.time() - start_time)

	cv2.rectangle(img_canvas, (best_x, best_y), (best_x+best_w, best_y+best_h), (0,0,255), 2)
	cv2.rectangle(map_canvas, (best_x, best_y), (best_x+best_w, best_y+best_h), (0,0,255), 2)

	cv2.imshow('Image', img_canvas)
	cv2.imshow('Saliency', map_canvas)
	key = cv2.waitKey(0)

	cv2.destroyAllWindows()


def main():
	saliency_crop('source/101.jpg', 'map/101.jpg', True)


if __name__ == "__main__":
	main()
