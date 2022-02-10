export project=ATLASMLHPO

echo "This is the current working directory"
pwd

echo "This is the current working directory"
ls

echo "This is the home directory"
ls /
echo "This is the parent folder of the working directory"
ls ..

if [ -w `pwd` ]; then echo "Current folder is writable"; else echo "Current folder is NOT writable"; fi

python ./train_mnist.py -i ./input.json -o ./output.json
