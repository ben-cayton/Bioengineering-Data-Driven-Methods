# -*- coding: utf-8 -*-
"""be 481 Project 2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14EFbrQVKp-YNEmzVaUs6Uoj6iUtepZQl
"""

# Linear algebra
import numpy as np
# Data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd
# Filter, discrete cosine transform and power spectrum density
from scipy import signal, fftpack
# MATLAB files
import scipy.io as sio
# Create a path to the directory
from os.path import dirname, join as pjoin
# Used to normalize
from wfdb import processing
# Training and testing dataset splitter
from sklearn.model_selection import train_test_split
# The learning model
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import StackingClassifier

#############################################################################  <-- 77 characters 
# Create a variable for the DataFrame 'train.csv' which has two columns:
# "Id" (the [  ] image file names in the training set) and "Expected"
# (labels 0 or 1, ).
df_train = pd.read_csv('../input/be-481-project-02/proj2/train.csv')
# Store the pathway to the train folder, which contains the training image
# files, in a variable.
directory_train = '../input/be-481-project-02/proj2/train'
# Create an empty array for the features with dimensions equal to the
# number of images by the number of features being used.
x = np.zeros([df_train.shape[0],12])
# Create an  array containing the labels of the training files.
y = np.array(df_train["Expected"])
# Loop through the training file names in the DatarFrame "df_train"
# in order that they are in the DataFrame. Extract the features.
for idx, filename in enumerate(df_train["Id"]):
    # Cretae a variable for the current filename.
    filenames = pjoin(directory_train, filename)
    # Load the MATLAB filetype.
    sig = sio.loadmat(filenames)
    # Create an array for the signal.
    data_arr = sig['data']
    # Extract the nested array
    data = data_arr[0]
    # Call the qrs indices from the preliminarily created csv file.
    qrs_inds_df = pd.read_csv('../input/qrs-indices/qrs_%s.csv' %
                           filename[:-4])
    # Reduce the qrs indices into a 1 dimensional array.
    qrs_inds = np.squeeze(qrs_inds_df.to_numpy())
    # Calculate the distances between qrs indices.
    qrs_dist = qrs_inds[1:] - qrs_inds[:-1]
    # Calculate the heart rate of the current file.
    hr_nan = wfdb.processing.compute_hr(len(data), qrs_inds, 250)
    # Replace NaN types and negative / positive infinity values with zero.
    hr = np.nan_to_num(hr_nan, copy=False, nan=0.0, posinf=0.0,
                       neginf=0.0)
    # Create a variable for the signal peaks.
    qrs = data[qrs_inds]
    # Calculate the area under a QRS complex.
    qrs_area = qrs[1:] / qrs_dist
    # Generate the power spectrum density
    f, pwr = signal.periodogram(data, fs=250)
    # Calculate the mean of the high frequencies.
    pwr_h = np.mean(pwr[pwr >= .03])
    # Calculate the mean of the low frequencies.
    pwr_l = np.mean(pwr[pwr < .03])
    # Calculate the ratio of high to low frequencies.
    pwr_rat_nan = pwr_l / pwr_h
    # Replace NaN types and negative / positive infinity values with zero.
    pwr_rat = np.nan_to_num(pwr_rat_nan, copy=False, nan=0.0, posinf=0.0,
                            neginf=0.0)
    # Create a variable for the indices of each peak in the current file.
    peaks_inds_arr = processing.find_peaks(data)
    # Extract the nested array.
    peaks_inds = peaks_inds_arr[0]
    # Create a variable for the signal corresponding to the indices of
    # each peak. 
    peaks = data[peaks_inds]
    # Calculate the distance between each peak.
    peaks_dist = peaks_inds[1:] - peaks_inds[:-1]
    # Redefine the element of "x" corresponding to the loop index as
    # the feature.
    x[idx,0] = np.mean(hr)
    x[idx,1] = np.mean(qrs_dist) / x[idx,0]
    x[idx,2] = np.std(qrs_dist) / x[idx,0]
    x[idx,3] = np.mean(peaks_dist) / x[idx,0]
    x[idx,4] = np.std(peaks_dist) / x[idx,0]
    x[idx,5] = np.mean(peaks) / x[idx,0]
    x[idx,6] = np.std(peaks) / x[idx,0]
    x[idx,7] = np.mean(qrs_area) / x[idx,0]
    x[idx,8] = np.std(qrs_area) / x[idx,0]
    x[idx,9] = pwr_h
    x[idx,10] = pwr_l
    x[idx,11] = pwr_rat
# Split off a random array of 20% of the data as the validation set.
x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2)
# Train the model on the 80% of the data set aside for training.
estimators = [
    ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
    ('svr', make_pipeline(StandardScaler(),
                          LinearSVC(random_state=42,  max_iter=10000)))
]
clf = StackingClassifier(
    estimators=estimators, final_estimator=LogisticRegression()
)
clf.fit(x_train, y_train)
# Print the accuracy of the predictions of the traind model on the
# validation set
print('Test accuracy: {0}'.format(clf.score(x_val, y_val)))

# Create a variable for the DataFrame 'test.csv' which has two columns:
# "Id" (the .png image file names in the test set) and "Expected" 
# (labels 0 or 1), this time only the column containing the filenames 
# will be used.
df_test = pd.read_csv('../input/be-481-project-02/proj2/sample-submission.csv')
# Store the pathway to the test folder, which contains the test image files, 
# in a variable.
directory_test = '../input/be-481-project-02/proj2/test'
# Re-create an empty array for the features with dimensions equal to the number
# of testing images by the same number of features used to train.
x = np.zeros([df_test.shape[0],12])
# Loop through the file names in the same way as with training. 
# Extract the features.
for idx, filename in enumerate(df_test["Id"]):
    filenames = pjoin(directory_test, filename)
    sig = sio.loadmat(filenames)
    data_arr = sig['data']
    data = data_arr[0]
    qrs_inds_df = pd.read_csv('../input/test-qrs-indxs/test_qrs_%s.csv' % 
                           filename[:-4])
    qrs_inds = np.squeeze(qrs_inds_df.to_numpy())
    qrs_dist = qrs_inds[1:] - qrs_inds[:-1]
    hr_nan = wfdb.processing.compute_hr(len(data), qrs_inds, 250)
    hr = np.nan_to_num(hr_nan, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    qrs = data[qrs_inds]
    qrs_area = qrs[1:] / qrs_dist
    f, pwr = signal.periodogram(data, fs=250)  
    pwr_h = np.mean(pwr[pwr >= .01])
    pwr_l = np.mean(pwr[pwr < .01])
    pwr_rat_nan = pwr_l / pwr_h
    pwr_rat = np.nan_to_num(pwr_rat_nan, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    peaks_inds_arr = processing.find_peaks(data)
    peaks_inds = peaks_inds_arr[0]
    peaks = data[peaks_inds]
    peaks_dist = peaks_inds[1:] - peaks_inds[:-1]
    x[idx,0] = np.mean(hr)
    x[idx,1] = np.mean(qrs_dist) / x[idx,0]
    x[idx,2] = np.std(qrs_dist) / x[idx,0]
    x[idx,3] = np.mean(peaks_dist) / x[idx,0]
    x[idx,4] = np.std(peaks_dist) / x[idx,0]
    x[idx,5] = np.mean(peaks) / x[idx,0]
    x[idx,6] = np.std(peaks) / x[idx,0]
    x[idx,7] = np.mean(qrs_area) / x[idx,0]
    x[idx,8] = np.std(qrs_area) / x[idx,0]
    x[idx,9] = pwr_h
    x[idx,10] = pwr_l
    x[idx,11] = pwr_rat
# Store the predicted labels in an array.
pred = clf.predict(x)
# Create a DataFrame with the same format as the sample submission,
# with column headers "Id", and "Predicted" which contain the file 
# names in the test set and their corresponding predicted labels.
df = pd.DataFrame({"Id":df_test["Id"],"Predicted":pred})
df.to_csv('out_four.csv', index=False)