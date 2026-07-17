# Terraform, full study document

Everything covered so far, in the order it actually happened, for proper review.

---

## Day 1, Wednesday: Infrastructure as Code, the concepts

### What problem needs solving?
At the moment, still manually having to provision servers. Provisioning means setting up and configuring servers.

### What have we automated so far?
Looking specifically at VMs:
- Creation of the VMs themselves? No, still manual
- Creation of the infrastructure they live in (VPC, subnets)? No, still manual
- Setup and configuring of software on the VMs once they exist? Yes, via bash scripting, user data, and images

So everything automated up to this point only covers what runs on a VM after it already exists. Nothing about creating the VM or the infrastructure around it has been automated.

### Solving the problem
IaC can automate all of it, both the parts marked "no" above. How? By codifying requirements.

Two approaches:
- **Imperative**, define every step in order (this is what all the bash scripts have been doing all along)
- **Declarative**, just declare what you want the end result to be, the tool works out the steps itself

### What is IaC?
A way to manage and provision resources, often computers, through a machine-readable definition of the infrastructure.

### Benefits of IaC
- Speed and simplicity
- Consistency and accuracy
- Version control
- Scalability

### When and where to use IaC
Return on investment, is it worth it? Not automatically the right call everywhere, there's setup overhead, so it comes down to whether the payoff justifies that investment for a given use case.

### What tools are available for IaC?
Two distinct categories:

**Configuration management (software configuration)**
- Chef
- Puppet
- Ansible

**Orchestration (managing infrastructure)**
- Terraform (cloud-agnostic)
- Cloud-specific alternatives:
  - Azure, ARM/Bicep templates
  - AWS, CloudFormation

### Provisioning vs configuration management
Provisioning means creating the actual infrastructure, the servers, networks, and storage themselves. Configuration management tools like Ansible are built for configuring what already exists, not creating it from scratch. Some CM tools can technically provision too, but it's not their primary job.

---

## Practical setup, Wednesday

### Installing Terraform on Windows
Checked the official HashiCorp install page, latest stable version at the time was 1.15.8.

```powershell
Invoke-WebRequest -Uri "https://releases.hashicorp.com/terraform/1.15.8/terraform_1.15.8_windows_amd64.zip" -OutFile "$env:TEMP\terraform.zip"
New-Item -ItemType Directory -Force -Path "C:\my-cmd-line-tools"
Expand-Archive -Path "$env:TEMP\terraform.zip" -DestinationPath "C:\my-cmd-line-tools" -Force
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\my-cmd-line-tools", "User")
```

Closed and reopened terminal, confirmed with:
```powershell
terraform --version
```
Output: `Terraform v1.15.8 on windows_amd64`

Also confirmed installed on RHEL:
```bash
sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install terraform
```
Output on RHEL: `Terraform v1.15.8 on linux_arm64`

### Private repo for Terraform code
Created `tech610-hoda-terraform` on GitHub, private, specifically to be the working repo Terraform commands actually run from, separate from the general training repo.

### AWS credentials as environment variables
Set as **User** environment variables (not system), values from a CSV, names had to be exact:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Verified in a fresh Git Bash window with `printenv`.

### AWS credential lookup order, worst to best security-wise
1. Env variables, mediocre unless temporarily pulled from something like a key vault
2. Hardcoded directly in a `.tf` file's `provider` block, worst, never do this
3. AWS CLI shared credentials file (from `aws configure`), mediocre
4. IAM role attached to the EC2 instance itself, best, no credentials stored anywhere at all

---

## Day 2, Thursday: Intro to Terraform specifically

### What is Terraform?
- An IaC orchestration tool
- An infrastructure provisioning tool
- Manages cloud resources
- Originally inspired by AWS CloudFormation
- Different to configuration management tools like Ansible, which deploy software onto servers that already exist
- Sees infrastructure as immutable, disposable, meaning if something's wrong the instinct is to destroy and recreate from code rather than patch it manually in place
- Uses code written in HCL (HashiCorp Configuration Language), designed to be a good balance between human and machine readable
- HCL can be converted 1:1 to JSON and back

### Why use Terraform, the benefits
- Declarative, say what you want, not how to do it
- Easy to use
- Sort of open source. In 2023 Terraform moved to Business Source License (BSL), meaning it can't be used to build a competing commercial product. Some organisations have since started using OpenTofu instead, a drop-in replacement that stayed fully open source
- Cloud-agnostic, deploys to any cloud provider using different providers, like plugins, to interface with each one. Each cloud vendor maintains its own provider
- Expressive (the language) and extendable (able to manage many different resource types via different providers)

### Alternatives to Terraform
- Pulumi (described as not declarative in the same way, since it's written in general-purpose programming languages)
- AWS CloudFormation
- Azure ARM/Bicep templates
- GCP Deployment Manager

### Who uses Terraform in industry
Examples spanning nearly every sector, showing it's not niche: Spotify, Airbnb, Coinbase, JPMorgan Chase, Goldman Sachs, Capital One, AWS itself, New Relic, Netflix, UK Government Digital Service, NASA.

### Giving Terraform access to different cloud providers

**AWS**, credential lookup order as above.

**Azure**
- Quickest way from a workstation: install Azure CLI
- Important restriction: only create resources inside the resource group already assigned, trying to create your own resource group results in a permissions error

**GCP**
1. Install `gcloud` CLI
2. `gcloud init` to log in
3. `gcloud auth application-default login` to create Application Default Credentials (ADC)

No credentials file needed when using ADC, Terraform picks it up automatically.

### Why use Terraform across different environments
- **Production**, easily create a larger-scale or more scalable version of the same infrastructure
- **Dev and testing**, easily spin up infrastructure that mirrors production, and easily tear it down again when not needed

---

## How Terraform works

Core dependency handling: Terraform automatically works out setup and teardown order by understanding the dependencies between resources, never has to be told the sequence manually.

### The diagram
Our laptop/PC contains:
- Terraform itself installed (`terraform.exe`), with commands `init`, `plan`, `apply`, `destroy`, `fmt`
- File/folder organisation: a project folder containing `*.tf` files (e.g. `main.tf`), `terraform.tfstate` (state, described as backup), `terraform.lock.hcl` (version lock), and a `.terraform/` folder that stores provider files locally
- A plugins layer, containing a separate provider per cloud (AWS provider, Azure provider, GCP provider), each provider talks to that cloud's own API (AWS APIs, ARM APIs, GCP APIs), which then reaches the actual cloud

### terraform init
Non-destructive, safe to run repeatedly. Checks the provider and checks the backend (where the state file itself will be stored). Never touches real infrastructure.

### Non-destructive vs destructive commands
- Non-destructive: `init`, `plan`, `fmt`
- Destructive (actually change real infrastructure): `apply`, `destroy`

---

## First code-along: creating an EC2 instance

Initial version:

```hcl
provider "aws" {
  region = "eu-west-1"
}

resource "aws_instance" "test_vm" {
  ami           = "ami-0c1c30571d2dae5c9"
  instance_type = "t3.micro"
  tags = {
    Name = "tech610-hoda-tf-first-vm"
  }
}
```

### Breaking down the syntax
- `resource` is the keyword saying "create something"
- `"aws_instance"` is the resource type, tells the AWS provider specifically to make an EC2 instance
- `"test_vm"` (the second string) is a local nickname used internally in the code, not the same as the actual AWS instance name
- Inside the block, `ami`, `instance_type`, and `tags` set the actual properties, same choices as the console's launch wizard, just written as key-value pairs

### terraform plan
Shows an execution plan before touching anything. `+` means create, `~` means change, `-` means destroy. Fields marked `(known after apply)` are things AWS itself generates once the resource actually exists, like `public_ip` or `id`, Terraform can't know them in advance.

The note at the bottom about `-out` means plan output isn't guaranteed to match exactly what apply does later unless the plan is saved to a file first, since real infrastructure could change in between.

### terraform apply
Runs the same plan, then requires typing `yes` to actually proceed, this confirmation is what makes running apply directly (without a separate plan step first) still safe, the gate is the `yes` prompt, not the existence of a prior plan.

### terraform destroy
Reverse of apply, removes everything Terraform is tracking, requires `yes` to confirm, warns there's no undo.

### Bug hit: wrong AWS account
After running apply, could not find the created instance in the console. Checked `terraform show`, found the instance's ARN referenced a different AWS account number than the one normally used. Checked `echo $AWS_ACCESS_KEY_ID`, came back empty, meaning credentials were actually being pulled from the AWS CLI's shared credentials file (`~/.aws/credentials`) instead, and that file held outdated or incorrect keys. Fixed by running `aws configure` again with the correct keys, confirmed with `aws sts get-caller-identity`, then re-ran the instance creation.

---

## .gitignore for Terraform

Ramon's version, built live with comments explaining reasoning:

```
# Local .terraform directories
# don't want provider files - they add bloat
.terraform/

# .tfstate files
# they can contain creds
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# .tfvars files, likely to contain sensitive data
*.tfvars
*.tfvars.json

# Override files, usually used to override resources locally
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Transient lock info files
.terraform.tfstate.lock.info
```

Also available as GitHub's official maintained template:
```bash
curl -s https://raw.githubusercontent.com/github/gitignore/main/Terraform.gitignore -o .gitignore
```

Important distinction: `.terraform.lock.hcl` is deliberately **not** in this list, it should be committed, not ignored, since it pins the exact provider version for consistency.

---

## Task: security group creation

Requirements: create a security group named with a `-tf-` suffix, allow port 22 from local IP only, ports 3000 and 80 from anywhere, then attach it plus a key pair to the existing instance.

```hcl
provider "aws" {
  region = "eu-west-1"
}

resource "aws_security_group" "tech610_hoda_tf_allow_port_22_3000_80" {
  name        = "tech610-hoda-tf-allow-port-22-3000-80"
  description = "Allow SSH from my IP, and ports 3000 and 80 from anywhere"

  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["194.80.254.16/32"]
  }

  ingress {
    description = "Port 3000 from anywhere"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Port 80 from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tech610-hoda-tf-allow-port-22-3000-80"
  }
}

resource "aws_instance" "test_vm" {
  ami                    = "ami-0c1c30571d2dae5c9"
  instance_type          = "t3.micro"
  key_name               = "hodas-tech610"
  vpc_security_group_ids = [aws_security_group.tech610_hoda_tf_allow_port_22_3000_80.id]

  tags = {
    Name = "tech610-hoda-tf-first-vm"
  }
}
```

### New concepts
- Each `ingress` block is one inbound rule. `cidr_blocks = ["x.x.x.x/32"]` means exactly one IP, the `/32` means no other addresses in that range are included
- `egress` had to be written explicitly, Terraform does not auto-add an allow-all outbound rule the way the AWS console does by default, skipping it entirely would mean no outbound traffic at all
- `key_name` attaches a key pair by its name already registered in AWS, not a file path
- `vpc_security_group_ids = [aws_security_group.xxx.id]` is how one resource references another. Terraform automatically works out the security group needs to exist before the instance, no manual ordering required

### Bug hit: IP address changed
SSH connection timed out after applying. Checked local IP again, found it had changed since the rule was written. The security group only trusted the exact IP given at the time. Updated `cidr_blocks` to the new IP, ran `plan` then `apply` again, only the security group's rule changed, the instance itself was untouched, confirming Terraform correctly identifies what's actually different versus what isn't.

Lesson: locking SSH to a single IP is more secure than leaving it open to everyone, but it's a live tradeoff, if that IP changes, access breaks silently until the rule is manually updated to match.

---

## Task: variables for all EC2 instance values

Requirement: convert every hardcoded value on the app instance into a variable.

`variables.tf`:
```hcl
variable "test_vm_ami_id" {
  description = "The AMI ID for my test EC2 instance"
  default     = "ami-0c1c30571d2dae5c9"
}

variable "test_vm_instance_type" {
  description = "Instance type for the test EC2 instance"
  default     = "t3.micro"
}

variable "test_vm_key_name" {
  description = "Key pair name for the test EC2 instance"
  default     = "hodas-tech610"
}

variable "test_vm_name_tag" {
  description = "Name tag for the test EC2 instance"
  default     = "tech610-hoda-tf-first-vm"
}
```

`main.tf`, instance block updated to reference variables instead of hardcoded values:
```hcl
resource "aws_instance" "test_vm" {
  ami                    = var.test_vm_ami_id
  instance_type          = var.test_vm_instance_type
  key_name               = var.test_vm_key_name
  vpc_security_group_ids = [aws_security_group.tech610_hoda_tf_allow_port_22_3000_80.id]

  tags = {
    Name = var.test_vm_name_tag
  }
}
```

### Syntax
- `variable "name" { }` declares a variable
- `description` is documentation only, doesn't affect execution
- `default` is the value used unless something else overrides it
- `var.name` is how a variable is referenced anywhere else in the code, always needs the `var.` prefix

### Bug hit: missing variable declaration
After adding three new variables, `terraform plan` failed with "Reference to undeclared input variable" for `test_vm_ami_id`. That variable had been left out when the file was edited, even though `main.tf` still referenced it. Fixed by adding the missing `variable "test_vm_ami_id" { }` block back into `variables.tf`. Lesson: every `var.name` reference in `main.tf` needs a matching `variable` declaration somewhere, Terraform won't infer one from the reference alone.

### Note on the instance no longer existing
After the instance was destroyed at the end of the security group task (standard cleanup), running `plan` again correctly showed "1 to add" rather than "0 to change", since Terraform's state had no record of any instance to compare against. This isn't a bug, it's Terraform correctly recognising that the previously tracked resource no longer exists.

---

## Still to come: 2-tier app deployment with Terraform

Full task, done in three parts:

**Part 1**: Terraform deploys the app VM only (frontend/local mode working). Terraform creates the app VM's security group, includes user data, uses the custom app AMI, and the correct key pair. Test by SSHing in after creation.

**Part 2**: Terraform also deploys the database VM (getting persistent/database mode working). Terraform creates the database VM's security group, uses the custom database AMI.

**Part 3**: Terraform deploys both app and database inside a custom VPC with 2 subnets, route tables, and an Internet Gateway, using the same CIDR blocks as the manually-built VPC from before, for higher database security.

Not yet started.
