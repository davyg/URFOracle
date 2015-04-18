# URFOracle

The main goal of this project was to use a neural network to predict from the
current-match endpoint if a team was going to win or lose its game. Since URF
is quite unbalanced the result could be good.

You have to insert your key in getid/getid.py, getMatch/getMatch.py and
learning/app.py depending on what you want to test. (there is a line in each
of theses files with key = "INSERT KEY")

There is 4 folder each one corresponding to a script :

## getId

This script grab from the api endpoint the bucket of match. It tries every
5 minutes to grab all the buckets from the last 8 hours(if they haven't been
already downlaoded). It does all the request with some delay to be sure
to respect the api limit.

I got 4108 buckets, this number corresponds to a bit more than 14 days which
must almost be all the bucket made available.

I forgot to mention that I only grabbed the buckets for euw but I could have
launched the script for each region.

All the files are put in the subfolder euw/ as a json file.

## getMatch

This script get all the ids from each bucket grab by the previous script
and retrieve all the corresponding data from the match endpoint and save
them in a file named by the id.

Like the previous script this script run continuously for the 15 days and I got
37238 match, which represent around 1G of data.URFOracle

## learning

In this folder you have two scripts : learning.py which use all the data grabed
to teach a neural network how to predict the winner and app.py a small website
that use the network to predict the result from the current-match endpoint.
The network file is used to store the neural network thanls to pickle python
lib.

The input dataset for the neural network is only the champs chosen and the
summoners, I would have eant to use also the masteries bans, and runes but I didn't
had the time. Rigth now I only managed to get a 47% error which is better than
answering at random but it wouldn't be noticeable for a human being.

The main problem I get from using a neural network is that it works well
with continuous data and not so well with discrete data(which is waht I have).
To avoid the problem instead of having an input champ1 containing the id of the
first champion. I used N inputs where N is the total number of champ. And among
theses inputs only one is put to one, the one corresponding to the first
champion. All the others are put to zero. And you have this for all the 10
champs and I did the same for the summoners.

Since I was too lazy to find the number of Champ, the number of real input
for each input is computed dynamically from the dataset. This is also good
because it is quite simple to add more input.

To implement the neural network I used a machine learning python library :
pyBrain. I run the learning on the 37000 match with 40 internal neurones.
I let the learning run for several hours. I did not made as many tests as I wanted
to get the best number of neuron and layer.

The website is implemented inFlask a python web framework and is really simple.

## stat

The last folder is a simple script that compute the statistic of win for each
champ from the big dataset I grabed. It was interesting to do that to check that
it make sense to hope that some broken champ could lead a team to the victory.
In the fact the stat does not mean that a champ is better that an other but that
if you have this champ in your team you have more chance to win. But it could
just mean that good players are more likely to choose this champ and they are
also more likely to win since they are good. There is a lot of scenari like
that. But for my purpose I don't care to know if a champ is broken I just want
to know the chance of winning whatever are the reason.

So for the stat I have a stat.py script that compute the percentage used and win
rate for each champ and save it into data.js. And then I have a index.html file
that used the data.js and display the data with a homemade css in a not so
fancy way. But you can see that some champ have really good chance of winning
and there is almost no correlation between the win rate and the usage rate.

## Conclusion

To conclude a lot more could have been done, to improve the result of the neural
network mainly by adding some inputs. But then the input size would have been
very big and the bigger it is the longer it takes to make some test to see
what is the best configuation and I did not had time for that. At least you get
the idea of what I wanted to do and the feasability but not so good result.