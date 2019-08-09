#Function:周一执行完全备份,其他时间执行增量备份,用tar压缩
import time
import os
import hashlib
import pickle
import tarfile

def check_md5(fname):
    m = hashlib.md5()

    with open(fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)

    return m.hexdigest()

def full_backup(src, dst, md5file):
    #完全备份,打tar包
    fname = '%s_full_%s.tar.gz' % (os.path.basename(src), time.strftime('%Y-%m-%d'))
    fname = os.path.join(dst, fname)

    tar = tarfile.open(fname, 'w:gz')
    tar.add(src)
    tar.close()

    #计算每个文件的md5值,并存入字典
    md5dict = {}
    for path, folers, files in os.walk(src):
        for file in files:
            key = os.path.join(path, file)
            md5dict[key] = check_md5(key)

    with open(md5file, 'wb') as fobj:
        pickle.dump(md5dict, fobj)

def incr_backup(src, dst, md5file):
    #增量备份,把改动文件打tar包
    fname = '%s_incr_%s.tar.gz' % (os.path.basename(src), time.strftime('%Y%m%d'))
    fname = os.path.join(dst, fname)

    #计算每个文件的md5值,并存入字典
    md5dict = {}
    for path, folers, files in os.walk(src):
        for file in files:
            key = os.path.join(path, file)
            md5dict[key] = check_md5(key)

    #取出之前文件的md5值
    with open(md5file, 'rb') as fobj:
        old_md5 = pickle.load(fobj)

    #将新增或有改动文件进行打包
    tar = tarfile.open(fname, 'w:gz')
    for key in md5dict:
        if old_md5.get(key) != md5dict[key]:
            tar.add(key)
    tar.close()

    #更新md5字典
    with open(md5file, 'wb') as fobj:
        pickle.dump(md5dict, fobj)

if __name__ == '__main__':
    src = '/var/lib/mysql'
    dst = '/tmp/backup'
    md5file = '/tmp/backup/md5.data'
    if not os.path.isdir(dst):
        os.mkdir(dst)

    if time.strftime('%a') == 'Mon':
        full_backup(src, dst, md5file)
    else:
        incr_backup(src, dst, md5file)