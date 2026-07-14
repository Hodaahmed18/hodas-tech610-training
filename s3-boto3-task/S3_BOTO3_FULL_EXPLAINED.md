# S3 and Boto3, everything from today

## What is S3 actually

S3 stands for Simple Storage Service. Basically it's a place in AWS where you can dump files (called objects) into containers (called buckets), and pull them back out whenever you want. No server involved, no file system to manage, you're not SSHing into anything to get your files, you're just talking to AWS's API.

Quick facts worth knowing:
- Every file you store lives in a bucket
- Bucket names have to be globally unique, not just unique to your account, unique across literally every AWS user on the planet
- AWS stores 3 copies of everything by default, spread across different Availability Zones (different physical data centers) in the same region, so if one data center has a bad day your data's still fine
- They advertise 99.999999999% durability, aka "11 nines", basically means your stuff isn't going anywhere
- You can talk to S3 three ways: the AWS Console (clicking around in the browser), the AWS CLI (typing commands in a terminal), or Python using a library called boto3 (writing actual code that does it for you)

## Part 1: doing it with the CLI

Before touching Python, we did this with plain terminal commands first, so here's that.

### Installing the CLI properly

Don't use whatever's shown in random tutorial videos, they're usually built for an older Ubuntu version and the commands don't match. Go straight to AWS's actual docs instead. Here's what actually worked:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

Breaking that down line by line:

- `curl "..." -o "awscliv2.zip"`: curl just grabs a file from a URL. The `-o` flag means "save it with this filename" so it downloads AWS's installer and calls it `awscliv2.zip`
- `sudo apt install unzip -y`: installs the tool that can actually open zip files, since Ubuntu doesn't come with one by default. `-y` just auto-confirms the "do you want to install this, yes/no" prompt so it doesn't sit there waiting for you
- `unzip awscliv2.zip`: unzips the file you just downloaded, creates a folder called `aws` full of installer files
- `sudo ./aws/install`: runs the actual install script inside that folder. `sudo` because installing software system-wide needs admin rights
- `aws --version`: just checks it worked, should print something like `aws-cli/2.35.22` back at you

### Authenticating

```bash
aws configure
```

This asks you four questions one at a time: your Access Key ID, your Secret Access Key, your default region, and your default output format. Access keys are basically your username and password but for programmatic access instead of logging into a website. Once you type these in, they get saved to a file on your machine (`~/.aws/credentials`) and every future `aws` command automatically uses them, you don't have to log in again each time.

### The actual S3 commands

`aws s3 ls`
Lists every bucket you have access to. `ls` is just "list", same as listing files in a normal folder.

`aws s3 ls | grep <name>`
The `|` is called a pipe, it takes the output of the first command and feeds it into the second one instead of printing it to the screen. `grep` searches through text for a specific word, so this filters your massive bucket list down to just the ones matching whatever you typed.

`aws s3 mb s3://bucket-name`
`mb` means "make bucket". Creates a new one.

`aws s3 cp local-file s3://bucket-name/`
`cp` means "copy", exactly like copying a file normally, except one side is your computer and the other side is S3.

`aws s3 sync local-folder/ s3://bucket-name/`
Like `cp` but for a whole folder at once, and smarter, it only copies files that are actually new or changed instead of re-copying everything every time.

`aws s3 rm s3://bucket-name/file-name`
`rm` means "remove". Deletes one specific file from a bucket.

`aws s3 rb s3://bucket-name --force`
`rb` means "remove bucket". On its own it refuses to delete a bucket that still has stuff in it, `--force` tells it to delete everything inside first and then the bucket itself.

## Part 2: doing the exact same thing with Python (boto3)

Boto3 is AWS's official Python library. Same underlying API as the CLI, same credentials file it reads from, just written as actual Python code instead of terminal commands. The task was to write six separate scripts, one job each, kept dead simple with no error handling.

### Setup first

```bash
sudo apt install python3-pip -y
pip3 install boto3 --break-system-packages
```

- `pip3` is Python's package installer, same idea as `apt` but for Python libraries specifically instead of whole programs
- `--break-system-packages` is needed because newer Ubuntu versions try to stop you installing Python packages system-wide by default, this flag just says "yes I know what I'm doing, install it anyway"

Since `aws configure` was already done earlier, boto3 automatically picks up those same saved credentials. You don't configure it separately, it just works.

### Script 1: list_buckets.py

```python
import boto3

s3 = boto3.client('s3')
response = s3.list_buckets()

for bucket in response['Buckets']:
    print(bucket['Name'])
```

- `import boto3`: pulls in the library so Python actually knows what `boto3` means
- `s3 = boto3.client('s3')`: creates a "client", basically an object that knows how to talk to the S3 part of AWS specifically. You're saving it into a variable called `s3` so you can reuse it
- `response = s3.list_buckets()`: actually calls AWS and asks for a list of every bucket. AWS sends back a big chunk of data (technically a dictionary), and we're saving the whole thing into a variable called `response`
- `for bucket in response['Buckets']:`: the response isn't just a plain list of names, it's a dictionary with a key called `'Buckets'`, and the value behind that key is a list of dictionaries, one per bucket, each containing details like name, creation date etc. This line loops through that list one bucket at a time
- `print(bucket['Name'])`: each individual bucket is itself a dictionary, and it has a key called `'Name'`. This grabs just the name and prints it out, ignoring all the other details you didn't ask for

### Script 2: create_bucket.py

```python
import boto3

s3 = boto3.client('s3')
s3.create_bucket(
    Bucket='tech610-hoda-test-boto3',
    CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
)
```

- First two lines are the same as before, import the library, make a client
- `s3.create_bucket(...)`: calls the function that actually creates a bucket
- `Bucket='tech610-hoda-test-boto3'`: this is the name you're giving it, has to be globally unique like mentioned earlier
- `CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}`: this tells AWS which region to physically put the bucket in. Weirdly, if your region isn't `us-east-1` (AWS's original default region), you have to explicitly say this or it'll throw an error, that's just an AWS quirk you have to know about

### Script 3: upload_file.py

```python
import boto3

s3 = boto3.client('s3')
s3.upload_file('testfile.txt', 'tech610-hoda-test-boto3', 'testfile.txt')
```

- `s3.upload_file(...)` takes three things in this order: the file on your local machine you want to upload, the name of the bucket you're sending it to, and what you want the file to be called once it's inside the bucket (called the "key" in S3 language). Here it's just kept the same name on both sides for simplicity, but they don't have to match

### Script 4: download_file.py

```python
import boto3

s3 = boto3.client('s3')
s3.download_file('tech610-hoda-test-boto3', 'testfile.txt', 'downloaded_testfile.txt')
```

- `s3.download_file(...)` is basically the reverse, also three things: which bucket to pull from, the key of the file inside that bucket, and what to name the file once it's saved on your local machine. Named it `downloaded_testfile.txt` here just so you could tell the two files apart and prove it actually pulled a fresh copy down

### Script 5: delete_file.py

```python
import boto3

s3 = boto3.client('s3')
s3.delete_object(Bucket='tech610-hoda-test-boto3', Key='testfile.txt')
```

- `s3.delete_object(...)` deletes one specific file. Note it's called `delete_object` not `delete_file`, that's just AWS's naming, since technically everything in S3 is called an "object" not a "file"
- `Bucket=...` which bucket it's in, `Key=...` which file inside that bucket

### Script 6: delete_bucket.py

```python
import boto3

s3 = boto3.client('s3')
s3.delete_bucket(Bucket='tech610-hoda-test-boto3')
```

- `s3.delete_bucket(...)` deletes the bucket itself. Only works if the bucket is already empty, which is why the file had to be deleted first in script 5 before this one could run

## Order they actually get run in

1. `list_buckets.py` first, just to see what's already there and confirm the whole setup is authenticated properly
2. `create_bucket.py` makes the new bucket
3. `upload_file.py` puts a test file inside it
4. `download_file.py` pulls that same file back down to prove the round trip works
5. `delete_file.py` empties the bucket out
6. `delete_bucket.py` removes the now-empty bucket completely

## Bugs I hit today

**Typo during `aws configure`**: accidentally typed `q` where the access key should've gone. Fixed by just running `aws configure` again and typing the real key properly, each field gets overwritten fresh every time you run it, nothing gets permanently broken from one bad entry.

**`aws s3 rb --force` said `NoSuchBucket`**: turned out the bucket had already been deleted, there was just nothing left to remove. Checked with `aws s3 ls | grep <name>` first next time to confirm what actually still exists before trying to delete it.

## Why this matters beyond just today

The CLI and boto3 are doing the literal same thing under the hood, they're both just different ways of hitting AWS's API. CLI is faster for quick one-off stuff you're typing by hand. Boto3 is what you'd actually use inside a real application, like if your app needs to automatically upload a user's profile picture to S3 the second they upload it, that's not something you'd type into a terminal, that's code running as part of the app itself. Same with your tictactoe app storing marker images, that pattern (`USE_MARKER_IMAGES`, `MARKER_IMAGES_PATH`) is exactly what boto3-style S3 access would look like wired into a real app.
