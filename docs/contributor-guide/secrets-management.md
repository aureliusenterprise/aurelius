# Secrets Management

This guide explains how to manage secrets in the project repository. Secrets are sensitive information that should
not be shared publicly. This includes API keys, passwords, and other sensitive data. Since we rely on secrets
for testing and deployment, it is important to share them securely.

## Getting started

The development container includes all the tools you need to manage secrets. We use [`SOPS`](https://github.com/getsops/sops)
to manage secrets in the repository. This tool allows us to encrypt and decrypt configuration files easily.

??? QUESTION "How do I identify encrypted files?"

    Encrypted files have the `.enc` extension. For example, the `.env.enc` file is an encrypted version of the
    `.env` file.

During initial setup of the development container, a unique key pair consisting of a public and a private key
is generated for you. It is stored in the `secrets/keys.txt` file.

??? QUESTION "I lost my key pair. What should I do?"

    You can generate a new key pair by running the following command:

    ```bash
    nx keygen
    ```

!!! DANGER "Security Warning"

    Only your public key can be safely shared. Do not share the private key with anyone!

## Registering a new key pair

To register a new key pair, extend the `.sops.yaml` file in the project root directory. Add your **public** key
to the list of `age` keys. Each key is separated by a comma and a newline.

```yaml
creation_rules:
    - age: >-
          <KEY1>,
          <KEY2>,
          <KEY3>
```

Next, create a new branch and commit your changes. After pushing the branch to GitHub, create a pull request to
merge the changes into the `main` branch. A GitHub action will automatically rotate the encryption on all encrypted
files in the repository to include your public key. After a team member approves the pull request, you can merge
the changes.

!!! NOTE "Ensure a descriptive pull request title"

    The pull request title should clearly indicate that you are adding a new key pair, and for which user it is intended.
    This helps in tracking who has access to the secrets in the repository.

Once the pull request is merged, pull the changes to your local repository. You can now decrypt and encrypt secrets
using your private key.

## Decrypting Secrets

Once the encryption on the files you need to access has been rotated, you can decrypt them using your private
key.

!!! TIP "Automatic Decryption with Nx"

    Every project that uses encrypted settings has an `Nx` target to decrypt the settings. Decryption is run automatically
    when you run the `serve`, `test`, or `e2e` targets.

If you need to decrypt the settings manually, you can run the following command:

```bash
nx decrypt <project-name>
```

Replace `<project-name>` with the name of the project you are working on. This will decrypt the `.env.enc` file
and save the contents to a corresponding `.env` file.

!!! DANGER "Security Warning"

    Do not commit your decrypted `.env` file to version control or share the contents with anyone!

## Encrypting Secrets

To encrypt the `.env` file after making changes, run the following command:

```bash
nx encrypt <project-name>
```

Replace `<project-name>` with the name of the project you are working on. This will encrypt the `.env` file for
that project and save the contents to a corresponding `.env.enc` file.
