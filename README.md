## Flickr Image Cropping Dataset

This repository contains the dataset used in the following paper:

Yi-Ling Chen, Tzu-Wei Huang, Kai-Han Chang, Yu-Chen Tsai, [Hwann-Tzong Chen](http://www.cs.nthu.edu.tw/~htchen/), [Bing-Yu Chen](http://graphics.csie.ntu.edu.tw/~robin/). (2017). ["Quantitative Analysis of Automatic Image Cropping Algorithms:A Dataset and Comparative Study"](http://arxiv.org/abs/1701.01480). IEEE Winter Conference on Applications of Computer Vision (WACV) 2017.

**If you use this dataset in an academic paper, please cite the following article:**

    @inproceedings{chen-wacv2017,
      title={Quantitative Analysis of Automatic Image Cropping Algorithms:A Dataset and Comparative Study},
      author={Yi-Ling Chen and Tzu-Wei Huang and Kai-Han Chang and Yu-Chen Tsai and Hwann-Tzong Chen and Bing-Yu Chen},
      booktitle={WACV 2017},
      year={2017}
    }

For more information regarding the paper, please visit https://yiling-chen.github.io/flickr-cropping-dataset/

## Download the dataset

1. Clone the repository to your local disk.
2. Under a command line terminal, run the following commands to get the images with cropping annotations:
```bash
$ cd scripts/
$ python download_images.py -w 4
```
The above command will launch 4 worker thread to download the images to a pre-defined folder (../data) from Flickr. Check out the code to see how to change the default folder. If you want to get the images with ranking annotation, run the following command instead.
```bash
$ python download_ranking_images -w 4
```

## Annotation

1. Cropping: `cropping_training_set.json` and `cropping_testing_set.json` contain the cropping annotations of this dataset. The annotations are saved as an array of JSON dictionaries. Each dictionary includes the information of one image. See the following for an example.

```json
[
    {
        "url":"https://farm5.staticflickr.com/4096/4910188666_04cf9f487d_b.jpg",
        "flickr_photo_id":4910188666,
        "crop":[
            266,
            6,
            757,
            399
        ]
    },
]
```

2. Ranking: `ranking_annotation.json` contain the ranking annotations of this dataset. The annotations are saved as an array of JSON dictionaries. Each dictionary includes the information of one image. Each image contains ten crop pairs. The crop with more votes is more visually pleasing than the other one. See the following for an example.

```json
[
    {
        "url":"https://farm3.staticflickr.com/2946/15251367120_9bdca6b5c3_c.jpg",
        "crops":[
            {
                "vote_for_1":1,
                "vote_for_0":4,
                "crop_1":[
                    171,
                    281,
                    300,
                    400
                ],
                "crop_0":[
                    139,
                    234,
                    300,
                    400
                ]
            },
        ],
        "flickr_photo_id":15251367120
    },
]
```

## License
MIT License


## Questions?
If you have questions/suggestions, please feel free to send an email to (yiling dot chen dot ntu at gmail dot com).
