import cv2
import numpy as np
from os import listdir
from os.path import isfile, join

source_images_path = './source/'
saliency_map_path = './map/'

def saliency_crop(img_filename, sal_filename):
	img = cv2.imread(join(source_images_path, img_filename))
	sal_map = cv2.imread(join(saliency_map_path, sal_filename), cv2.IMREAD_GRAYSCALE)
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
	best_avg_sal = -1.0

	# uniform scaling
	scales = [0.5, 0.7, 0.9]
	for scale in scales:
		w = int(width * scale)
		h = int(height * scale)
		#print w, h

		# generate the grid vertices of sliding windows
		X = [x for x in range(0, width, 5) if x < width - w]
		Y = [y for y in range(0, height, 5) if y < height - h]

		for x in X:
			for y in Y:
				# TODO: use integral image to speed up
				avg_sal = np.sum(sal_map[y:y+h, x:x+w])/float(w * h)
				if avg_sal > best_avg_sal:
					best_x = x
					best_y = y
					best_w = w
					best_h = h
					best_avg_sal = avg_sal

	print best_x, best_y, best_w, best_h, best_avg_sal

	cv2.rectangle(img_canvas, (best_x, best_y), (best_x+best_w, best_y+best_h), (0,0,255), 2)
	cv2.rectangle(map_canvas, (best_x, best_y), (best_x+best_w, best_y+best_h), (0,0,255), 2)

	cv2.imshow('Image', img_canvas)
	cv2.imshow('Saliency', map_canvas)
	key = cv2.waitKey(0)

	cv2.destroyAllWindows()


def main():
	saliency_crop('101.jpg', '101.jpg')

if __name__ == "__main__":
	main()
