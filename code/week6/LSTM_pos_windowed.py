import sys
import numpy as np
import re
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import LSTM, Embedding, Reshape, TimeDistributed, Bidirectional,InputLayer,Activation
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import plot_model

import tensorflow
import tensorflow.keras.backend as K
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
from keract import get_activations


filename = sys.argv[1]

pos_tagged_text = open(filename, 'r', encoding='ISO-8859-1').readlines()

Words={}
Tags={}

n_words=0
n_sentences=0

maxlen=0

for line in pos_tagged_text:
        if line[0]==' ':
            next
        n_sentences+=1
        words=line.rstrip().lower().split(" ")
        l=len(words)        
        if l>maxlen:
                maxlen=l
        n_words+=l
        if words[0]=='':
            next
        for word in words:
            m=re.match("^([^\_]+)\_([^\s]+)",word)
            if m:
                word=m.group(1)
                tag=m.group(2)
                Words[word]=1
                Tags[tag]=1

words = sorted(Words)
tags=sorted(Tags)
vocab_len=len(Words)+1
print(tags)

word_to_int = dict((w, i+1) for i, w in enumerate(words))
word_to_int[0]=0 # padding
int_to_word = dict((i+1, w) for i, w in enumerate(words))
int_to_word[0]=0 # padding

tag_to_int = dict((t, i+1) for i, t in enumerate(tags))
tag_to_int[0]=0 # padding 
int_to_tag = dict((i+1, t) for i, t in enumerate(tags))
int_to_tag[0]=0 # padding

X=[]
y=[]

focus_position=3

for line in pos_tagged_text:
        if line[0]==' ':
            next
        sent=[]
        words=line.rstrip().lower().split(" ")
        n=1
        int_tag=0
        if words[0]=='':
            next
        for word in words:
            m=re.match("^([^\_]+)\_(.+)",word)            
            if m:
                word=m.group(1)
                tag=m.group(2)
                sent.append(word_to_int[word])
                if n==focus_position:                    
                    int_tag=tag_to_int[tag]
            n+=1
        X.append(sent)
        y.append(int_tag)

      

X = pad_sequences(X, maxlen=maxlen, padding='post')
#y = pad_sequences(y, maxlen=maxlen, padding='post')

X=np.array(X)
y=np.array(y)

model = Sequential()
model.add(InputLayer(input_shape=(maxlen, )))
model.add(Embedding(vocab_len, 128))
model.add(Bidirectional(LSTM(256, return_sequences=False)))
model.add(Dense(len(Tags)+1))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(0.001),
              metrics=['accuracy'])

model.summary()


#plot_model(model, to_file='LSTM_pos_model.png')


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)


#X_train=np.array(X_train)
#y_train=np.array(y_train)

model.fit(X_train,to_categorical(y_train),epochs=2,batch_size=64)

model.evaluate(X_test,to_categorical(y_test))

predictions=model.predict(X_test)

n=0
for sentence in X_test:
        sentence_prediction=predictions[n]
        n+=1
        best_tag=int_to_tag[np.argmax(sentence_prediction,axis=0)]
        m=1
        for int_word in sentence:
            if m==focus_position:
                print("<<%s_%s>>"%(int_to_word[int_word],best_tag),end=" ")
            else:
                print(int_to_word[int_word],end=" ")
            m+=1
        print()
              
