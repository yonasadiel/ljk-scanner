from matplotlib import pyplot as plt
import numpy as np
import cv2
import math
import sys, glob, time
import ljk_grader

IMG_WIDTH = 1000
LJK_RATIO = 19.2/26
ROW = 62
COL = 46
MIN_CIRCULARITY = 0.75
FILLED_PERCENTAGE = 50
CELL_MARGIN = 0.2
FILE_NAME = 'output.dat'

def findFourKeyPoint(img, circularity):
  # find 4 keypoint from image with known minimum circularity
  # on the blob detector
  params = cv2.SimpleBlobDetector_Params()

  params.filterByCircularity = True
  params.minCircularity = circularity
  params.maxCircularity = 1

  params.filterByConvexity = True
  params.minConvexity = 0.85

  params.filterByArea = True
  params.minArea = img.shape[0]*img.shape[1]//10000

  det = cv2.SimpleBlobDetector_create(params)
  kp = det.detect(img)

  if (len(kp) == 0):
    return [], []

  hull = cv2.convexHull(cv2.KeyPoint_convert(kp))
  points = [[img.shape[0], img.shape[1]],[0, img.shape[1]],[img.shape[0], 0],[0, 0]]
  for i in hull:
    if (i[0][0] + i[0][1] < points[0][0] + points[0][1]): points[0] = i[0]
    if (i[0][0] - i[0][1] > points[1][0] - points[1][1]): points[1] = i[0]
    if (i[0][0] - i[0][1] < points[2][0] - points[2][1]): points[2] = i[0]
    if (i[0][0] + i[0][1] > points[3][0] + points[3][1]): points[3] = i[0]

  return kp, points

def detectAndWrapCorner(img_src):
  img = img_src.copy()
  blur_radius = IMG_WIDTH//100*2+1
  img = cv2.GaussianBlur(img_src, (blur_radius, blur_radius), 0)
  r, img = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)

  # binary search the exact circularity for find exactly 4 keypoints
  kp, points = findFourKeyPoint(img, MIN_CIRCULARITY)

  img_with_keypoints = cv2.drawKeypoints(img_src, kp, np.array([]), (0, 0, 255),
                                        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
  # cv2.imshow('image', img_with_keypoints)
  # cv2.waitKey(0)

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
  out_size = (IMG_WIDTH, int(IMG_WIDTH/LJK_RATIO))
  offset = (out_size[0]/COL/2, out_size[1]/ROW/2)
  dst = np.array([[              offset[0],               offset[1]],
                  [out_size[0] - offset[0],               offset[1]],
                  [out_size[0] - offset[0], out_size[1] - offset[1]],
                  [              offset[0], out_size[1] - offset[1]]],
                  dtype=np.float32)

  matrix = cv2.getPerspectiveTransform(points, dst)

  transform = cv2.warpPerspective(img_src, matrix, out_size)

  return transform

def getOnlyBlueChannel(img_src):
  out_image = cv2.split(img_src)[0]
  return out_image

def getCoordinateFromIndices(img, row, col):
  t_row = img.shape[0]
  t_col = img.shape[1]

  r = int(row * t_row / ROW)
  c = int(col * t_col / COL)

  return r,c

def isFilled(img, row, col):
  width = int(IMG_WIDTH / (COL))

  r_top, c_lft = getCoordinateFromIndices(img, row, col)
  r_btm = r_top + width
  c_rgt = c_lft + width

  r_top += int(CELL_MARGIN * width)
  c_lft += int(CELL_MARGIN * width)
  r_btm -= int(CELL_MARGIN * width)
  c_rgt -= int(CELL_MARGIN * width)

  cnt_black = 0
  for r_i in range(r_top, r_btm+1):
    for c_i in range(c_lft, c_rgt+1):
      if (img[r_i][c_i] < 120):
        cnt_black += 1

  return (cnt_black / ((r_btm - r_top)*(c_rgt - c_lft)) >= FILLED_PERCENTAGE / 100)

def createAnswerMatrix(img):
  offset = int(IMG_WIDTH / (COL)/ 2)
  ljk_mat = [[0 for i in range(COL)] for j in range(ROW)]
  for i in range(0,ROW):
    for j in range(0, COL):
      r,c = getCoordinateFromIndices(img, i,j)
      if (isFilled(img, i, j)):
        cv2.rectangle(img, (c, r), (c+offset*2, r+offset*2), 128, 5)
        ljk_mat[i][j] = 1
  return ljk_mat

def printToFile(obj):
  (
    nama_peserta, nomor_peserta, kode_soal,
    kode_sekolah, kode_cabang,
    pilihan_1, pilihan_2, pilihan_3,
    jawaban, kode_kelas, mata_ujian, materi_ujian
  ) = obj

  ans = ''.join(jawaban)

  fout = open(FILE_NAME, 'a+')
  fout.write(
    nama_peserta + '\t' +
    nomor_peserta + '\t' +
    kode_soal + '\t' + 
    kode_sekolah + '\t' + 
    kode_cabang + '\t' +
    pilihan_1 + '\t' +
    pilihan_2 + '\t' +
    pilihan_3 + '\t' +
    ans + '\t' +
    kode_kelas + '\t' +
    mata_ujian + '\t' +
    materi_ujian + '\n'
  )
  fout.close()

def processImage(img_in):
  if (img_in.all() == None):
    print('file not found')
    return None

  img_ori_height = img_in.shape[0]
  img_ori_width  = img_in.shape[1]
  img_ratio      = img_ori_width / img_ori_height

  img_in = cv2.resize(img_in, (IMG_WIDTH, int(IMG_WIDTH/img_ratio)))

  img_grey = getOnlyBlueChannel(img_in)
  
  img_th = cv2.adaptiveThreshold(img_grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2. THRESH_BINARY, 25, 12)
  
  img_wrp = detectAndWrapCorner(img_th)

  ljk_mat = createAnswerMatrix(img_wrp)

  printToFile(ljk_grader.processMatrix(ljk_mat))

  return img_wrp

def main(folder_name):
  time_start = time.time()

  for file_name in glob.glob(folder_name + '/*.jpg'):
    img_in = cv2.imread(file_name)
    img_out = processImage(img_in)

    cv2.imwrite(file_name[:-4] + "-out.jpeg", img_out)
    print('[%8.3f] %s processed' % (time.time() - time_start, file_name))

if __name__ == '__main__':
  errcode = 0
  usage = 'Usage: python ljk_scanner.py foldername'

  if (len(sys.argv) < 2):
    print(usage)
  elif (len(sys.argv) < 3):
    main(sys.argv[1])
  else:
    print(usage)
