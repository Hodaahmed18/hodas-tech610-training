# Setting up Terraform, what it is and how I installed it

## What is Terraform, and what is IaC

IaC stands for Infrastructure as Code. Instead of clicking through the AWS console by hand to build a VPC, launch an instance, set up a security group, all of that, you write it down in config files instead, and a tool reads those files and builds the actual infrastructure for you. If you want to rebuild the exact same setup again, or hand it to someone else, or destroy it cleanly, it's all just running the same files again rather than trying to remember and repeat every click you did manually.

Terraform is HashiCorp's tool for doing this. It works across basically any cloud provider (AWS, Azure, GCP, and loads more), you write your infrastructure in `.tf` files using a language called HCL (HashiCorp Configuration Language), then Terraform reads those files and talks to the provider's API to actually create the resources.

Why this matters after everything already built manually this course: every VPC, subnet, EC2 instance, and security group so far has been built by hand, clicking through the console or typing individual CLI commands. Terraform is the next step up from that, the same infrastructure, but described in a file that can be version controlled, reused, and rebuilt identically any time.

## Where Terraform actually runs

Worth being clear on this since it wasn't obvious to me at first. Terraform isn't something that needs to live on an EC2 instance or anywhere in the cloud. It's a command line tool that runs on whatever machine you're sitting at, your own laptop, or an instance you're SSH'd into, doesn't matter. It just needs three things present wherever you run it from: the `terraform` binary itself installed, your `.tf` config files, and your AWS credentials configured so it's allowed to actually make changes on your behalf. Terraform then reaches out to AWS's API and creates/changes/destroys resources remotely, the same way the AWS CLI does, it's not running anything on the machine it's installed on beyond the tool itself.

## Installing Terraform on Windows

Checked the official HashiCorp Terraform install page first, latest stable version at the time was 1.15.8.

Downloaded the Windows zip directly in PowerShell:

```powershell
Invoke-WebRequest -Uri "https://releases.hashicorp.com/terraform/1.15.8/terraform_1.15.8_windows_amd64.zip" -OutFile "$env:TEMP\terraform.zip"
```

`Invoke-WebRequest` is PowerShell's version of `curl`, downloads a file from a URL. `-Uri` is the download link, `-OutFile` says where to save it, `$env:TEMP` is just a shortcut PowerShell already knows, points at the Windows temp folder, so I didn't need to type the full path out by hand.

Made a dedicated folder to keep all my command line tools in one logical place, rather than scattering executables across random folders:

```powershell
New-Item -ItemType Directory -Force -Path "C:\my-cmd-line-tools"
```

`New-Item` creates a new file or folder, `-ItemType Directory` says specifically a folder not a file, `-Force` means don't throw an error if it already exists, just carry on.

Extracted the zip straight into that folder:

```powershell
Expand-Archive -Path "$env:TEMP\terraform.zip" -DestinationPath "C:\my-cmd-line-tools" -Force
```

`Expand-Archive` is PowerShell's unzip command. `-Path` is the zip file to open, `-DestinationPath` is where to put the extracted contents, `-Force` again just means overwrite anything already there without asking.

Added that folder to my PATH permanently, so any terminal window, opened from anywhere, knows to look there when I type `terraform`:

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\my-cmd-line-tools", "User")
```

Breaking this one down since it looks intimidating: `[Environment]::SetEnvironmentVariable(...)` is calling a method that sets an environment variable. First argument `"Path"` says which variable we're changing. Second argument `$env:Path + ";C:\my-cmd-line-tools"` takes my existing PATH value and tacks the new folder onto the end of it, separated by a semicolon (that's how Windows separates entries in a PATH list). Third argument `"User"` means this change applies to my own user account, not the whole machine system-wide.

## Verifying it actually worked

PATH changes don't apply to terminal windows that were already open before you made the change, they only get picked up by brand new windows. So I closed PowerShell completely and opened a fresh one, then ran:

```powershell
terraform --version
```

Output:
```
Terraform v1.15.8
on windows_amd64
```

This confirms two things at once: Terraform is actually installed correctly, and it's accessible from any terminal window, any folder, not just from inside the folder I extracted it to. That second part matters, if I'd only been able to run it from inside `C:\my-cmd-line-tools` itself, the PATH step wouldn't have actually worked.

## What I'd do differently on Linux (RHEL/Ubuntu)

Since I might end up doing the actual Terraform exercises from my RHEL instance instead of Windows, the install there is different but the same overall idea:

```bash
sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install terraform
terraform --version
```

`yum-utils` and `shadow-utils` are just prerequisite packages the repo setup needs. `yum-config-manager --add-repo` tells the system's package manager about HashiCorp's official repository, so `yum install terraform` afterward knows where to actually pull the package from, rather than trying to find it somewhere it doesn't exist. No PATH setup needed here, since installing via `yum` automatically puts the binary somewhere already on the system PATH.

## Summary

- IaC means describing infrastructure in code instead of building it by hand through the console
- Terraform is the tool, works across most cloud providers, uses `.tf` files written in HCL
- Terraform runs locally, wherever you are, and talks to AWS's API remotely, it isn't something that needs to be installed on the infrastructure it's managing
- Installed version 1.15.8 on Windows manually via the zip, added it to PATH so it works from any terminal
- Confirmed working with `terraform --version` from a fresh terminal window
- Noted the equivalent install steps for RHEL in case exercises end up running from there instead
