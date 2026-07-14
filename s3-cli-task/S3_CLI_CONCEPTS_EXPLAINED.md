# S3 and the CLI, concepts and commands

## What is S3

S3 stands for Simple Storage Service. It's AWS's object storage, meaning you store files (called objects) inside containers (called buckets), and there's no server or file system sitting underneath it that you have to manage. You're not SSHing anywhere to get your files, you're just talking to AWS directly.

Key concepts:

**Bucket**
A container that holds your files. Bucket names have to be globally unique, not just unique within your own account, unique across every single AWS user that exists. That's why generic names like `test-bucket` are basically always already taken.

**Object**
The actual file sitting inside a bucket. AWS calls it an object rather than a file because technically it could be anything, a text file, an image, a video, a chunk of data, doesn't matter, it's all just an object once it's in S3.

**Region**
The physical location AWS puts your bucket in, e.g. `eu-west-1` is Ireland. Matters for latency and for legal/data residency reasons in some cases.

**Availability Zone (AZ)**
A physically separate data center within a region. S3 automatically stores 3 copies of every object, spread across different AZs in the same region, so if one data center has an outage your data's still safe elsewhere.

**Durability**
AWS advertises 99.999999999% durability for S3, known as "11 nines". Basically means the odds of actually losing your data are close enough to zero that it's not a realistic concern.

**Static website hosting**
S3 buckets can be configured to directly serve a website, HTML/CSS/JS files sitting in a bucket, no EC2 instance or web server needed at all. Useful for simple sites that don't need any backend logic.

**Three ways to access S3**
- AWS Console, clicking around in the browser
- AWS CLI, typing commands in a terminal
- SDKs like Python's boto3, writing code that talks to S3 programmatically

This doc covers the CLI side specifically.

## Setting up the CLI

### Installing it properly

Don't trust random tutorial videos for the install commands, they're often written for an older Ubuntu version and won't work right. Go straight to AWS's actual documentation instead.

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

What each line does:

- `curl "..." -o "awscliv2.zip"`: downloads AWS's installer file from their URL, `-o` just tells it what to name the downloaded file
- `sudo apt install unzip -y`: installs the tool needed to open zip files, since Ubuntu doesn't come with one pre-installed. `-y` auto-confirms the install prompt
- `unzip awscliv2.zip`: extracts the installer files into a folder called `aws`
- `sudo ./aws/install`: actually runs the install script, needs `sudo` since it's installing system-wide
- `aws --version`: confirms it worked, prints back a version number

### Authenticating

```bash
aws configure
```

Asks for four things: Access Key ID, Secret Access Key, default region, default output format. Access keys are basically a username and password, but built for programmatic access rather than logging into a website through a browser. Once entered, they get saved locally and every future `aws` command automatically uses them without asking again.

Check it's working:
```bash
aws s3 ls
```
Should list your buckets with no error, confirming credentials and region are both set up right.

## Core commands, what they mean

**`aws s3 ls`**
Lists all your buckets. `ls` is short for "list", same word used for listing files in a normal directory.

**`aws s3 ls | grep <search-term>`**
The `|` is called a pipe. It takes the output of whatever's on the left and feeds it as input into whatever's on the right, instead of just printing it straight to the screen. `grep` searches text for a match, so piping your bucket list into `grep` filters it down to just the ones containing that search term.

**`aws s3 mb s3://bucket-name`**
`mb` stands for "make bucket". Creates a new bucket with that name.

**`aws s3 ls s3://bucket-name/`**
Lists everything sitting inside one specific bucket, rather than listing all your buckets.

**`aws s3 cp local-file s3://bucket-name/`**
`cp` means "copy", same idea as copying any file, except here one side is your local machine and the other is S3. Works both directions depending on which path you put first.

**`aws s3 sync local-folder/ s3://bucket-name/`**
Like `cp` but for a whole folder, and smarter about it, only transfers files that are actually new or have changed rather than blindly re-copying everything every single time. Add `--delete` on the end if you also want it to remove files on the destination that no longer exist on the source, so both sides end up identical.

**`aws s3 rm s3://bucket-name/file-name`**
`rm` means "remove". Deletes one specific file from inside a bucket.

**`aws s3 rb s3://bucket-name --force`**
`rb` means "remove bucket". By itself it refuses to delete a bucket that still has files in it. Adding `--force` tells it to delete every object inside first, then the bucket itself.

## Which command for which situation

| What you're trying to do | Command |
|---|---|
| See what buckets you have | `aws s3 ls` |
| See what's inside one specific bucket | `aws s3 ls s3://bucket-name/` |
| Make a brand new bucket | `aws s3 mb` |
| Move a single file up or down | `aws s3 cp` |
| Keep a whole folder and a bucket matching, only sending changes | `aws s3 sync` |
| Delete one file from a bucket | `aws s3 rm` |
| Delete a bucket and everything inside it | `aws s3 rb --force` |

## Bugs I actually hit

**Typo during `aws configure`, typed `q` instead of my real access key.**
Fixed it by just running `aws configure` again and typing the correct value. Each field gets overwritten fresh every time you run the command, so nothing was permanently broken, it just needed redoing properly.

**`aws s3 rb --force` threw a `NoSuchBucket` error.**
Turned out the bucket had already been deleted, there was nothing left there to remove. Ran `aws s3 ls | grep <name>` first to confirm what actually still exists before trying to delete something again.

## Why this actually matters

Everything here maps directly to what you'd do at a real company, just with a smaller blast radius. A company's app might use S3 to store uploaded user files, profile pictures, backups, static assets for a website, logs, anything. The CLI is what you'd reach for doing quick one-off admin tasks, checking what's in a bucket, pulling a file down to inspect it, cleaning something up manually. Once it's part of an actual running application though, that's where you'd move to something like boto3 instead, since an app can't sit there typing terminal commands, it needs to do this programmatically as part of its own code.
