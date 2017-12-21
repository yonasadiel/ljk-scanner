import sys, glob, time

ROW = 62
COL = 46
ALPHABET = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ? '
MATA_UJIAN = ['PPKN', 'B. INDONESIA', 'B. INGGRIS', 'SEJARAH',
              'GEOGRAFI', 'SOSIOLOGI', 'AKUNTANSI', 'EKONOMI',
              'FISIKA', 'KIMIA', 'BIOLOGI', 'MATEMATIKA', 'IPA', 'IPS', 'INVALID', '']
MATERI_UJIAN = ['TKPA', 'TKD SAINTEK', 'TKD SOSHUM', 'INVALID', '']
JAWABAN = 'ABCDE? '

def getMultipleChoicesToBottom(mat, top_offset, col, height):
  # [0,height) if ONLY ONE filled
  # -1 if blank
  # -2 if multiple
  ans = -1
  for row in range(top_offset, top_offset + height):
    if (mat[row][col] == 1):
      if (ans == -1):
        ans = row - top_offset
      else:
        ans = -2
  return ans

def getMultipleChoicesToRight(mat, left_offset, row, width):
  # [0,width) if ONLY ONE filled
  # -1 if blank
  # -2 if multiple
  ans = -1
  for col in range(left_offset, left_offset + width):
    if (mat[row][col] == 1):
      if (ans == -1):
        ans = col - left_offset
      else:
        ans = -2
  return ans

def getNamaPeserta(mat):
  nama = ''
  for col in range(1,1 + 20):
    row = getMultipleChoicesToBottom(mat, 4, col, 27)

    poss = '*'
    if (row == 0):
      poss = ' '
    elif (row > 0):
      poss = chr(ord('A') + row-1)
    elif (row == -1):
      poss = ' '
    elif (row == -1):
      poss = '?'

    nama += poss
  return nama.rstrip()

def getNomorPeserta(mat):
  nomor_peserta = ''
  for col in range(22, 22 + 11):
    if (col != 22 + 5):
      row = getMultipleChoicesToBottom(mat, 8, col, 10)
      if (row >= 0):
        nomor_peserta += str(row)
      elif (row == -1):
        nomor_peserta += ' '
      elif (row == -2):
        nomor_peserta += '?'
  return nomor_peserta.rstrip()

def getBasicField(mat, left_offset, top_offset, length, height):
  ret = ''
  for col in range(left_offset, left_offset + length):
    row = getMultipleChoicesToBottom(mat, top_offset, col, height)
    if (row >= 0):
      ret += str(row)
    elif (row == -1):
      ret += ' '
    elif (row == -2):
      ret += '?'
  return ret.rstrip()

def getJawabanCoordinate(number):
  number -= 1
  col =  2 + (number // 25) * 6
  row = 33 + number % 25

  return row, col

def getJawaban(mat):
  jawaban = [' ' for i in range(150)]
  for i in range(1, 150+1):
    row, col_start = getJawabanCoordinate(i)
    idx = getMultipleChoicesToRight(mat, col_start, row, 5)
    jawaban[i-1] = JAWABAN[idx] 
  return jawaban

def processMatrix(mat):
  nama_peserta  = ''.join([ALPHABET[getMultipleChoicesToBottom(mat, 4, i, 27)] for i in range(1, 1 + 20)]).rstrip()
  nomor_peserta = getNomorPeserta(mat)
  kode_soal     = getBasicField(mat, 34,  8, 3, 10)
  kode_sekolah  = getBasicField(mat, 38,  8, 8, 10)
  kode_cabang   = getBasicField(mat, 22, 21, 3, 10)
  pilihan_1     = getBasicField(mat, 26, 21, 6, 10)
  pilihan_2     = getBasicField(mat, 33, 21, 6, 10)
  pilihan_3     = getBasicField(mat, 40, 21, 6, 10)
  jawaban       = getJawaban(mat)
  kode_kelas    = getBasicField(mat, 38, 34, 4, 10)
  mata_ujian    = MATA_UJIAN[getMultipleChoicesToBottom(mat, 33, 42, 14)]
  materi_ujian  = MATERI_UJIAN[getMultipleChoicesToBottom(mat, 50, 39, 3)]

  return (
    nama_peserta, nomor_peserta, kode_soal,
    kode_sekolah, kode_cabang,
    pilihan_1, pilihan_2, pilihan_3,
    jawaban, kode_kelas, mata_ujian, materi_ujian
  )

def main(folder_name):
  time_start = time.time()
  ljk_mat = [[0 for i in range(COL)] for j in range(ROW)]
  
  for file_name in glob.glob(folder_name + '/*.jpg'):
    fin = open(file_name, 'r')
    for i in range(0,ROW):
      for j in range(0, COL):
        f.read(ljk_mat[i][j])

    (
      nama_peserta, nomor_peserta, kode_soal,
      kode_sekolah, kode_cabang,
      pilihan_1, pilihan_2, pilihan_3,
      jawaban, kode_kelas, mata_ujian, materi_ujian
    ) = processMatrix(ljk_mat)
    print('[%8.3f] %s processed' % (time.time() - time_start, file_name))

if __name__ == '__main__':
  errcode = 0
  usage = 'Usage: python ljk_grader.py foldername'

  if (len(sys.argv) < 2):
    print(usage)
  elif (len(sys.argv) < 3):
    main(sys.argv[1])
  else:
    print(usage)
