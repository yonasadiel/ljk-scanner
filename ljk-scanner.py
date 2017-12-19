from matplotlib import pyplot as plt
import numpy as np
import cv2
import math
import sys, glob

IMAGE_WIDTH = 1000

def findFourKeyPoint(img, circularity):
  # find 4 keypoint from image with known minimum circularity
  # on the blob detector
  params = cv2.SimpleBlobDetector_Params()

  params.filterByCircularity = True
  params.minCircularity = circularity
  params.maxCircularity = 1

  params.filterByConvexity = True
  params.minConvexity = 0.90

  params.filterByArea = True
  params.minArea = img.shape[0]*img.shape[1]//10000

  det = cv2.SimpleBlobDetector_create(params)
  kp = det.detect(img)

  hull = cv2.convexHull(cv2.KeyPoint_convert(kp))
  points = list()
  for i in hull:
      points.append(i[0])
  return kp, points


def detectAndWrapCorner(img_src):
  img = img_src.copy()
  img = cv2.GaussianBlur(img_src, (3, 3), 0)
  r, img = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)

  # binary search the exact circularity for find exactly 4 keypoints
  points = []
  kp = None
  counter = 0
  min_c = 0.5
  max_c = 1
  while (len(points) != 4 and counter < 100):
    mid_c = (min_c + max_c)/2
    kp, points = findFourKeyPoint(img, mid_c)

    if (len(points) < 4):
      max_c = mid_c
    elif (len(points) > 4):
      min_c = mid_c
    counter += 1

  if (counter == 100):
    print('> 100 loop on fnding keypoint')
    return None

  im_with_keypoints = cv2.drawKeypoints(img_src, kp, np.array([]), (0, 0, 255),
                                        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

  # sort clockwise from top-left
  def cmp(point):
      center = img.shape[1]/2, img.shape[0]/2
      if point[0] < center[0]:
          if(point[1] < center[1]):
              return 0
          else:
              return 3
      else:
          if(point[1] < center[1]):
              return 1
          else:
              return 2

  points = np.array(sorted(points, key=cmp), dtype=np.float32)
  out_size = (img.shape[1], img.shape[0])
  offset = out_size[0]/120
  dst = np.array([[offset, offset],
                  [out_size[0] - offset, offset],
                  [out_size[0] - offset, out_size[1] - offset],
                  [offset, out_size[1] - offset]],
                  dtype=np.float32)

  matrix = cv2.getPerspectiveTransform(points, dst)

  transform = cv2.warpPerspective(im_with_keypoints, matrix, out_size)

  return transform

def getOnlyBlueChannel(img_src):
  img_blue = img_src.copy()
  for i in range(len(img_blue)):
    for j in range(len(img_blue[i])):
      img_blue[i][j][1] = img_blue[i][j][0]
      img_blue[i][j][2] = img_blue[i][j][0]
  img_grey = cv2.cvtColor(img_blue, cv2.COLOR_BGR2GRAY)
  return img_grey

def processImage(img_in):
  if (img_in.all() == None):
    print('file not found')
    return None

  img_ori_height = img_in.shape[0]
  img_ori_width  = img_in.shape[1]
  img_ratio      = img_ori_width / img_ori_height

  img_in = cv2.resize(img_in, (IMAGE_WIDTH, int(IMAGE_WIDTH/img_ratio)))

  img_grey = getOnlyBlueChannel(img_in)
  
  img_th = cv2.adaptiveThreshold(img_grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2. THRESH_BINARY, 25, 12)

  img_wrp = detectAndWrapCorner(img_th)

  return img_wrp

def main(folder_name):
  for file_name in glob.glob(folder_name + '/*.jpg'):
    img_in = cv2.imread(file_name)
    img_out = processImage(img_in)

    plt.subplot(1,1,1),plt.imshow(img_out, 'gray')
    plt.xticks([]),plt.yticks([])
    plt.show()

    cv2.imwrite(file_name[:-4] + "-out.jpg", img_out)


if __name__ == '__main__':
  errcode = 0
  usage = 'Usage: python ljk-scanner.py foldername'

  if (len(sys.argv) < 2):
    print(usage)
  elif (len(sys.argv) < 3):
    errcode = main(sys.argv[1])
  else:
    print(usage)

  if (errcode != 0):
    print('exit with error code ' + str(errcode))