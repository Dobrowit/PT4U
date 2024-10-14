# PT4U - Power Tools for Ubuntu

  - UbuntuPL - Skrypt do szybkiego 🚀 wykonywania czynności poinstalacyjnych.
  - chkmousec - Pomaga ustalić ustawienia kursora myszy
  - debdesk - Checks .desktop files and which deb package they belong to.
  - desk2menu - Convert .desktop files to a Fluxbox menu.
  - smb2home - A script to quickly mount SMB resources from within your home directory.


# debdesk
Looks for .desktop files and checks if they work and checks which deb package they belong to.

![Zrzut ekranu z 2024-10-12 19-18-49](https://github.com/user-attachments/assets/575e04b7-d8b7-4ff0-a470-3f4e08010cdf)

# desk2menu
Massive conversion of .desktop files to a Fluxbox menu - with GUI.

TODO:
 - localize (English and Polish using .po files)

![Zrzut ekranu z 2024-10-11 09-27-19](https://github.com/user-attachments/assets/cc028c1d-1e1d-4b58-b483-186517bd7a2f)


# smb2home
A script to quickly mount SMB resources from within your home directory.
```
smb2home [option]
 <share>            Mount network share <share> for the current user
 <share> -u <user>  Mount network share <share> for the user <user>
 -a                 Mount all shares (from the list -ls)
 <share> -d         Unmount share <share>
 -da                Unmount all shares (from the list -ls)
 -ls                List shares on the server for the current user
 -ls -u <user>      List shares on the server for the user <user>
 -l                 List mounted shares
 -s <ip>            Save the SMB server address
 -p <user>          Save the password for the user <user>
 -i                 Configuration information
 -h                 Help
```

The share name <share> is not a full address. If the share has the address:

>  smb://192.168.0.10/myfiles

then for <share>, you enter:

>  myfiles


# DIRECTORY FOR MOUNTING SHARES

>  /home/user/mnt

If this directory does not exist, it will be created. Individual shares will be mounted in subdirectories named after the share. For a share named myfiles, the directory will be /home/user/mnt/myfiles.


# PASSWORD
The password for the specified user is retrieved from the keyring. If you do not provide a username, the current user will be used. To edit the keyring, use seahorse (GUI) or secret-tool (CLI). The password is searched by three keys:
```
  protocol = 'smb'
  user = user
  server = 192.168.0.10
```

You can add the password to the keyring using the Nautilus file manager. Mount the share. If prompted to remember the password, save it permanently. To edit and view stored passwords, use the seahorse application.

You can also use the command:

>  secret-tool store protocol smb user user server 192.168.0.10


# SERVER ADDRESS
The server address must be provided as an IP address or domain, e.g.:

>  192.168.0.10

You can change the address directly in this script, at the beginning in the variable SRV or by saving it in the file /home/user/.smb2home.


# USERNAME
You must provide a username if the current user is different from the one on the SMB server.
