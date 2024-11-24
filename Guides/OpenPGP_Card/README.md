# Using OpenPGP card

## Basic GPG commands

:arrow_forward: These commands apply to whole `gpg`, regardless if it's used with OpenPGP card or not.

### Encrypt file

```
gpg --output file.enc --encrypt --recipient <keyid or uid> file.plain
```

### Encrypt file symmetrically

```
gpg --output file.enc --symmetric file.plain
```

### Encrypt file while showing progress

```
pv < file.plain | gpg --verbose --output file.enc --recipient <keyid or uid> --encrypt -
```

### Decrypt file

```
gpg --output file.plain --decrypt file.enc
```

:arrow_forward: The same command can decrypt both standard- and symmetrically-encrypted files.

:arrow_forward: Decrypt calls can be piped together if there are multiple levels of encryption,like so:

```
gpg --decrypt input.dat | gpg --no-symkey-cache --output output.zip --decrypt
```

### Decrypt file while showing progress

```
pv < file.enc | gpg --verbose --output file.plain --decrypt -
```

## Setting up GPG and SSH for use with OpenPGP card

### Windows (WSL2 with Ubuntu/Debian)

1. Install latest [Gpg4win](https://gpg4win.org) on Windows.

2. Run `Kleopatra`, so that `Gpg4win` will do its initial setup. You may check if your OpenPGP card is visible in `Kleopatra` to make sure card communication works on Windows level.

3. Modify `Gpg4win` configuration files. Create them if needed and don't leave newlines at the end.

```
$ cat /mnt/c/Users/USER/AppData/Roaming/gnupg/gpg-agent.conf

enable-ssh-support
enable-putty-support
use-standard-socket
default-cache-ttl 1
max-cache-ttl 1
```

```
$ cat /mnt/c/Users/USER/AppData/Roaming/gnupg/gpg.conf

use-agent
```

4. Create a Windows shortcut to `gpg-connect-agent.exe` in some convenient place like the desktop. Edit it by adding `/bye` to `Target` field. It should look like this:

```
Target: "C:\Program Files (x86)\ GnuPG\bin\gpg-connect-agent.exe" /bye
```

5. Install requires packages in WSL:

```
sudo apt-get install gpg gpgconf socat iproute2 scdaemon
```

6. Install `wsl2-ssh-pageant`:

```
$ wget https://github.com/BlackReloaded/wsl2-ssh-pageant/releases/1.4.0/wsl2-ssh-pageant.exe -O $HOME/.ssh/wsl2-ssh-pageant.exe

$ chmod +x $HOME/.ssh/wsl2-ssh-pageant.exe
```

7. Add the following lines to `.bashrc`:

```
export SSH_AUTH_SOCK="$HOME/.ssh/agent.sock"
export GPG_AGENT_SOCK="$HOME/.gnupg/S.gpg-agent"
```

8. Create a script `setgpg.sh`, with the following contents:

```
#!/bin/bash
# REM MWGM 96285299|86079264

config_path="C\:/Users/USER/AppData/Local/gnupg"
wsl2_ssh_pageant_bin="$HOME/.ssh/wsl2-ssh-pageant.exe"

# You need to uncomment the line below for WSL1
#killall socat

# SSH socket
if ! ss -a | grep -q "$SSH_AUTH_SOCK"; then
  rm -f "$SSH_AUTH_SOCK"
  if test -x "$wsl2_ssh_pageant_bin"; then
    (setsid nohup socat UNIX-LISTEN:"$SSH_AUTH_SOCK,fork" EXEC:"$wsl2_ssh_pageant_bin --gpgConfigBasepath ${config_path}" >/dev/null 2>&1 &)
  else
    echo >&2 "WARNING: $wsl2_ssh_pageant_bin is not executable."
  fi
fi

# GPG Socket
if ! ss -a | grep -q "$GPG_AGENT_SOCK"; then
  rm -f "$GPG_AGENT_SOCK"
  if test -x "$wsl2_ssh_pageant_bin"; then
    (setsid nohup socat UNIX-LISTEN:"$GPG_AGENT_SOCK,fork" EXEC:"$wsl2_ssh_pageant_bin --gpgConfigBasepath ${config_path} --gpg S.gpg-agent" >/dev/null 2>&1 &)
  else
    echo >&2 "WARNING: $wsl2_ssh_pageant_bin is not executable."
  fi
fi
```

**Now, to run the setup and enable GPG and SSH cooperation with the OpenPGP card:**

1. Run your `gpg-connect-agent.exe` shortcut that you had created in point 3. You may need to run it several times, sometimes the agent is moody and doesn't want to get up the first time.
2. Open or restart `bash` terminal and run `setgpg.sh` script.
3. Insert your OpenPGP card to reader and make sure the interface works by running `gpg --card-status`.
4. If there are problems, try to kill GPG agent by running `"C:\Program Files (x86)\ GnuPG\bin\gpg-connect-agent.exe" killagent /bye` in `cmd.exe`. Then restart it by running your shortcut again.

**This procedure needs to be repeated after every Windows restart, if you want to use your OpenPGP card during that session.**

### Linux (Ubuntu/Debian)

1. Install required packages:

```
sudo apt-get install gpg gpgconf socat iproute2 scdaemon
```

2. Modify `gpg-agent.conf` configuration file. Create it if needed and don't leave newlines at the end.

```
$ cat ~/.gnupg/gpg-agent.conf

enable-ssh-support
default-cache-ttl 1
max-cache-ttl 1
```

3. Add the following lines to `.bashrc`:

```
export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
gpgconf --launch gpg-agent
```

4. Open or restart `bash` terminal.

5. Insert your OpenPGP card to reader and make sure the interface works by running `gpg --card-status`.

6. If there are problems, try to kill and restart GPG agent:

```
$ gpg-connect-agent killagent /bye
$ gpg-connect-agent /bye
```

### Git signing setup

First, you need to fetch public keys corresponding to your card's private keys to your `gpg` keyring. These public keys must be available on a well-known PKP keyserver such as [OpenPGP](https://keys.openpgp.org) or under URL explicitly configured on the card. You need to run the following commands:

```
$ gpg --card-edit
gpg/card> fetch
gpg/card> quit
```

To force Git to sign every commit with your OpenPGP's card signing key, you need to run the following commands:

```
$ git config --global user.name <user name matching key's uid>
$ git config --global user.email <user email matching key's uid>
$ git config --global commit.gpgsign true

# Note the exclamation mark
$ git config --global user.signingkey <signing subkey keyid>!

# Some Linux distros use gpg2 instead of gpg
$ git config --global gpg.program gpg
```
