# -*- coding: utf-8 -*-
"""22f1000725-notebook-t22024 (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/173IOU4TX-qN6iezjlbcdnb-UJAaO9rbC

# Importing necessary libararies
"""

import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

"""# loading the train and test data into dataframes"""

train = pd.read_csv("/content/train.csv (1).zip")
test=pd.read_csv("/content/train.csv (1).zip")

train.head() #to check if data has been loaded into the dataframe

train.shape  #checking the rows and features of the train data

test.shape  #checking the rows and features of test data

"""# Exploratory Data Analysis (EDA)"""

train.info()

"""* Cross_Street column has high number of missing values hence we can drop it."""

# Compute correlation matrix
correlation_matrix = train.select_dtypes(['float']).corr()

# Plot heatmap of the correlation matrix
plt.figure(figsize=(10, 5))
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
sns.heatmap(correlation_matrix,mask=mask, annot=True, cmap='coolwarm')
plt.show()

"""* Longtitude and Latitude have a negative correlation hence we can drop one of these columns.
* Area_ID and Reporting_District_no also have a high correlation and hence we can drop Reporting_District_no column.
"""

train['Crime_Category'].value_counts()

plt.figure(figsize=(20, 15))
sns.countplot(x='Crime_Category', data=train, palette='pastel')
plt.title('Distribution of Crime_Category')
plt.xlabel('Crime_Category')
plt.ylabel('Count')
plt.show()

"""### Maximum crimes are property crimes and least are other crimes and crimes against persons"""

train.describe()

# Histogram for Latitude and Longitude
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.hist(train['Latitude'].dropna(), bins=30, color='blue', alpha=0.7, edgecolor='black')
plt.title('Histogram of Latitude')
plt.xlabel('Latitude')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
plt.hist(train['Longitude'].dropna(), bins=30, color='green', alpha=0.7, edgecolor='black')
plt.title('Histogram of Longitude')
plt.xlabel('Longitude')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

"""### Outliers in Latitude and Longitude column are quite low so we can ignore them."""

train['Victim_Sex'].unique()

plt.figure(figsize=(8, 6))
sns.countplot(x='Victim_Sex', data=train, palette='pastel')
plt.title('Distribution of Victim Sex')
plt.xlabel('Victim Sex')
plt.ylabel('Count')
plt.show()

"""### Number of crimes are fairly eqaully distributed amongst the male and female category, also X can be interpeted as missing value."""

plt.figure(figsize=(8, 6))
sns.countplot(x='Victim_Descent', data=train, palette='pastel')
plt.title('Distribution of Victim Descent')
plt.xlabel('Victim Descent')
plt.ylabel('Count')
plt.show()

# Relationship between Victim Descent and Victim Sex
plt.figure(figsize=(10, 6))
sns.countplot(x='Victim_Descent', hue='Victim_Sex', data=train)
plt.title('Victim Descent vs Victim Sex')
plt.xlabel('Victim Descent')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.legend(title='Victim Sex', loc='upper right')
plt.show()

# Boxplot to show outliers in Victim Age
plt.figure(figsize=(8, 6))
sns.boxplot(y='Victim_Age', data=train)
plt.title('Boxplot of Victim Age')
plt.ylabel('Age')
plt.show()

"""### Count the number of missing values in the Weapon_Used_Code column for each combination of Crime_Category and Weapon_Used_Code."""

train.groupby(['Crime_Category', 'Weapon_Used_Code'])['Weapon_Used_Code'].apply(lambda x: x.isna().sum())

"""### A pattern in Weapon_Used_Code column based on the Crime_Category"""

train.isna().sum().sort_values(ascending=False)

test.isna().sum().sort_values(ascending=False)

"""### Null/missing values columns
* Cross_Street (can be ignored since we will drop it in future)
* Modus_Operandi
* Victim_Sex
* Victim_Descent
* Weapon_Used_Code
* Weapon_Description
* Premise_Description

# Feature Engineering

### Extracting useful columns from Date_Reported and Date_Occurred column
"""

# Define date format
date_format = '%m/%d/%Y %I:%M:%S %p'

# Convert date columns to datetime with specified format
train['Date_Reported'] = pd.to_datetime(train['Date_Reported'], format=date_format)
train['Date_Occurred'] = pd.to_datetime(train['Date_Occurred'], format=date_format)
test['Date_Reported'] = pd.to_datetime(test['Date_Reported'], format=date_format)
test['Date_Occurred'] = pd.to_datetime(test['Date_Occurred'], format=date_format)

# Calculate days delayed in report
train['Days_Delayed'] = (train['Date_Reported'] - train['Date_Occurred']).dt.days
test['Days_Delayed'] = (test['Date_Reported'] - test['Date_Occurred']).dt.days

#extract hour occured
train['Hour_Occurred'] = train['Time_Occurred'].apply(lambda x: int(x // 100))

#extract hour occured
test['Hour_Occurred'] = test['Time_Occurred'].apply(lambda x: int(x // 100))

train.shape

"""### We drop all the date and time related columns after extracting the useful deatures from it. We also drop the status description column as we are already retaining the status column."""

train.drop(columns=['Date_Reported', 'Date_Occurred', 'Time_Occurred',  'Status_Description'], axis=1, inplace=True)

test.drop(columns=['Date_Reported', 'Date_Occurred',  'Time_Occurred',  'Status_Description'], axis=1, inplace=True)

train['Weapon_Used_Code'].unique()

"""### Imputing Weapon_Used_Code column"""

from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='constant', fill_value=-1)

# Fit and transform the 'Weapon_Used_Code' column
train['Weapon_Used_Code'] = imputer.fit_transform(train[['Weapon_Used_Code']])

from sklearn.impute import SimpleImputer

# Fit and transform the 'Weapon_Used_Code' column
test.loc[:, 'Weapon_Used_Code'] = imputer.transform(test[['Weapon_Used_Code']])

train['Weapon_Used_Code'].isna().sum()

test['Weapon_Used_Code'].isna().sum()

"""### handling missing values in Categorical Columns

* number of unique values in the Modus_Operandi
"""

len(set(train.Modus_Operandi.fillna("MISSING").str.split().explode().tolist()))

categorical_columns = ['Modus_Operandi', 'Victim_Sex', 'Victim_Descent',]
values = ['mo_missing', 'X', 'X']
for column, v in zip(categorical_columns, values):
   train[column] = train[column].fillna(v)

for column, v in zip(categorical_columns, values):
    test.loc[:, column] = test[column].fillna(v)

train.isna().sum().sort_values(ascending=False)

test.isna().sum().sort_values(ascending=False)

np.corrcoef(train.Area_ID, train.Reporting_District_no)[0, 1]

"""#### Since these two columns have a high correlation we can drop one of them"""

np.corrcoef(train.Latitude, train.Longitude)[0, 1]

"""#### Latitude and Longitude have a negative correlation so we must drop one of these columns.

### Dropping columns with high number of missing values or negative/high correlation coefficient

* Premise_Description and Weapon_Description can also be dropped as we already have Premise_Code and Weapon_Used_Code
"""

train.columns.tolist()
drop_cols = ['Location', 'Cross_Street', 'Longitude', 'Area_Name', 'Reporting_District_no', 'Premise_Description', 'Weapon_Description']
train.drop(columns=drop_cols, axis=1).columns.tolist()

"""### Encoding target variable"""

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y = le.fit_transform(train['Crime_Category'])

"""### Scaling and Processing the numerical and categorical columns"""

from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer

cat_encoder=OneHotEncoder(sparse_output=False, handle_unknown='ignore')
num_encoder=MinMaxScaler()

num_col = ['Latitude',
                     'Victim_Age',
                     ]

cat_col = ['Weapon_Used_Code', 'Premise_Code',
                           'Victim_Sex', 'Victim_Descent',
                            'Status',  'Area_ID',]


ctf = ColumnTransformer(
    [
        ("num", num_encoder, num_col),
        ("cat", cat_encoder, cat_col),
    ],
    remainder="passthrough", verbose_feature_names_out=False
).set_output(transform='pandas')

ctf_mo = ColumnTransformer([('mo', Pipeline([('mo_v', CountVectorizer())]), 'Modus_Operandi')], remainder='passthrough', verbose_feature_names_out=False)
pipe = Pipeline([('ctf', ctf),
                 ('ctf_mo', ctf_mo),
                 ])

train = pipe.fit_transform(train.drop(columns=drop_cols+['Crime_Category'], axis=1))
train = pd.DataFrame(train, columns=pipe.named_steps['ctf_mo'].get_feature_names_out())

test = pipe.transform(test)
test = pd.DataFrame(test, columns=pipe.named_steps['ctf_mo'].get_feature_names_out())

train.shape, test.shape
#number of features added due to onehot encoding

train.isna().sum().sum(), test.isna().sum().sum()
#a final check for any missing values

"""# Splitting data into train and validation data"""

x_train, x_val, y_train, y_val = train_test_split(train, y, test_size=0.3, random_state=42)

x_train.shape, x_val.shape, y_train.shape, y_val.shape

"""# Model Training

# XGBClassifier model
"""

from xgboost import XGBClassifier
model = XGBClassifier(random_state=10, seed=10)
model.fit(x_train, y_train)
print(model.score(x_train, y_train), model.score(x_val, y_val))

"""### train data accuracy : 0.9972857142857143
### validation data accuracy : 0.9593333333333334
"""

from sklearn.metrics import classification_report
print(classification_report(y_val, model.predict(x_val), target_names=le.classes_))
classification_report_xgb=classification_report(y_val, model.predict(x_val), target_names=le.classes_, output_dict=True)

from sklearn.metrics import confusion_matrix
print(confusion_matrix(y_val, model.predict(x_val)))

"""# Support Vector Classifier"""

from sklearn.model_selection import cross_validate
from sklearn.svm import LinearSVC

# Define the model with an increased number of iterations
model_1 = LinearSVC(random_state=0, tol=1e-5, C=15.0, max_iter=10000)

# Fit the model
model_1.fit(x_train, y_train)

# Predict on the test set
predictions = model_1.predict(test)

# Calculate accuracy on the training and validation sets
accuracy = model_1.score(x_train, y_train)
acc = model_1.score(x_val, y_val)

print(accuracy, acc)

"""### train data accuracy : 0.9656428571428571
### test data accuracy : 0.943
"""

print(classification_report(y_val, model_1.predict(x_val), target_names=le.classes_))
classification_report_svm=classification_report(y_val, model_1.predict(x_val), target_names=le.classes_, output_dict=True)

print(confusion_matrix(y_val, model_1.predict(x_val)))

"""# Logistic Regression model"""

from sklearn.linear_model import LogisticRegression
model_2 = LogisticRegression(random_state=42)

model_2.fit(x_train, y_train)

# Predict on train and test data
logistic_predictions_train = model_2.predict(x_train)

# Evaluate the model
accuracy = model_2.score(x_train, y_train)
acc=model.score(x_val, y_val)
print(f'train accuracy is :{accuracy}\nvalidation data accuracy is :{acc}')

"""### train accuracy is :0.8233571428571429
### validation data accuracy is : 0.9593333333333334
"""

print(classification_report(y_val, model_2.predict(x_val), target_names=le.classes_))
classification_report_lr=classification_report(y_val, model_2.predict(x_val), target_names=le.classes_, output_dict=True)

print(confusion_matrix(y_val, model_2.predict(x_val)))

"""# Random Forest Classifier Model"""

# from sklearn.model_selection import GridSearchCV
# # Define the parameter grid
# param_grid = {
#     'n_estimators': [100, 200, 300],
#     'max_depth': [None, 10, 20, 30],
#     'min_samples_split': [2, 5, 10],
#     'min_samples_leaf': [1, 2, 4],
#     'bootstrap': [True, False]
# }

# # Define the RandomForestClassifier model
# rf = RandomForestClassifier(random_state=5)

# # Set up the grid search
# grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, verbose=1, n_jobs=-1)

# # Fit the model
# grid_search.fit(x_train,y_train)

# grid_search.best_params_

from sklearn.ensemble import RandomForestClassifier
model_3 = RandomForestClassifier(criterion = 'gini',
                               bootstrap=False,
                               max_depth=None,
                               min_samples_leaf=1,
                               min_samples_split=2,
                               n_estimators=300,
                               random_state=42)

model_3.fit(x_train, y_train)

# Evaluate the model
accuracy_train= model_3.score(x_train, y_train)
accuracy = model_3.score(x_val, y_val)
print(f'train data accuracy is :{accuracy_train} \nvalidation data accuracy is:{accuracy}')

"""### train data accuracy is :1.0
### validation data accuracy is:0.95
#### This model overfits on the train data
"""

print(classification_report(y_val, model_3.predict(x_val), target_names=le.classes_))
classification_report_rf=classification_report(y_val, model_3.predict(x_val), target_names=le.classes_, output_dict=True)

print(confusion_matrix(y_val, model_2.predict(x_val)))

"""# Model Comparison"""

models = ['Logistic Regression', 'SVM', 'Random Forest Classifier', 'XGBClassifier']
train_accuracy_scores = [0.823, 0.965, 0.100, 0.997]
validation_accuracy_scores = [0.959, 0.943, 0.950, 0.959]


# Creating the DataFrame
dict_score = {
    'Model': models * 2,
    'Metric': ['Train_Accuracy'] * len(models) + ['Validation_Accuracy'] * len(models),
    'Score': train_accuracy_scores + validation_accuracy_scores
}
df = pd.DataFrame(dict_score)

# Plotting
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.barplot(x='Score', y='Model', hue='Metric', data=df, palette='viridis')
plt.title('Model Comparison - Train and Validation data accuracy')
plt.xlabel('Score')
plt.ylabel('Model')
plt.show()

"""### Hence we can conclude that the XGBClassifier model works well on both train and validation data. So we will select the XGBClassifier as our best model."""

kagg_pred = model.predict(test)

kagg_pred.shape

pd.DataFrame({'ID': range(1, len(kagg_pred)+1),
              'Crime_Category': le.inverse_transform(kagg_pred)}).to_csv('submission.csv', index=False)

"""# Saving the model"""

import joblib
joblib.dump(model, 'model.pkl')

classifier=joblib.load('model.pkl')