import sys, glob, time

ROW = 62
COL = 46

def processMatrix(mat):
  nama_peserta = ''
  nomor_peserta = ''
  kode_soal = ''
  kode_sekolah = ''
  kode_cabang = ''
  pilihan_1 = ''
  pilihan_2 = ''
  pilihan_3 = ''
  jawaban = [' ' for i in range(150)]
  kode_kelas = ''
  mata_ujian = ''
  materi_ujian = ''

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