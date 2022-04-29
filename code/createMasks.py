import tensorflow as tf
import numpy as np
import os
import datetime
import time

from medpy.io import load, save
from buildModel import CNN
from dataHelper import GetDataSets
from DataSetNPY import DataSetNPY
from metrics import *
from globalVars import *

import sys

if len(sys.argv) < 2:
    print('usage: createMask <in_mri> <out_mask>')
    sys.exit()

in_mri = sys.argv[1]
out_mask = sys.argv[2]



def createMasks(fileNames, saveNames, checkpointDir=None):
    """
    Reloads a model from checkpointDir and runs it on the files
    specified in fileNames. For each file in fileNames,
    writes a mask whose filename is specified by saveNames.
    That is, the mask for fileNames[i] will be stored in saveNames[i].
    """
    if checkpointDir is None:
        checkpoints = os.listdir('../checkpoints')
        checkpointDir = '../checkpoints/' + np.sort(checkpoints)[-1] + '/'

    with tf.variable_scope('InputPlaceholders'):
        imageShape = [None, height, width, n_channels]
        imagesPL = tf.placeholder(dtype=tf.float32, shape=imageShape, name='imagesPL')

    #Build Model
    outputLayer = CNN(imagesPL)
    binaryOutputLayer = tf.argmax(outputLayer, axis=3)

    # Each individual medpy image is of shape (96, 96, 37)
    with tf.Session() as sess:
        saver = tf.train.Saver()
        saver.restore(sess, checkpointDir)
        print('Restored model from: {}'.format(checkpointDir))
        for i in range(len(fileNames)):
            fileName = fileNames[i]
            saveName = saveNames[i]
            start = time.time()
            image, header = load(fileName)
            image = np.transpose(image, (2, 0, 1))
            image = np.expand_dims(image, -1)

            #The predicted mask is of shape (37, 96, 96)
            predictedMask = sess.run(binaryOutputLayer, feed_dict={imagesPL: image})
            predictedMask = np.transpose(predictedMask, (1, 2, 0))
            save(predictedMask, saveName, header)
            end = time.time()
            print(end-start)
 
#AN EXAMPLE OF HOW TO USE THIS WITH AN ENTIRE DIRECTORY
#dir = '/Users/saigerutherford/Desktop/images/' #set this path to the directory where your input images live
#names = [name for name in os.listdir(dir)] 
#fileNames = [dir + name for name in names]
#saveNames = [dir + 'pred_' + name for name in names]
createMasks([in_mri],[out_mask])

#AN EXAMPLE WITH A SINGLE FILE
#fileNames = ['zpr_2006-T1_run1_vol0017.nii']
#saveNames = ['pred_zpr_2006-T1_run1_vol0017.nii']
#createMasks(fileNames, saveNames)
