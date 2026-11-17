---
title: I've lost my e-books
description: Kindle decide to move my stuff out. Is paper better than technology these
  days?
date: '2026-11-16'
image: /images/i-ve-lost-my-e-books-bcf08241-5d8e-4309-ad1b-d0f9cf0f7c77.png
tags:
- kindle ai recovery
draft: true
---

I thought that will be good idea to have some of my books in one virtual place avaliable i.e. when I'm wait for something out of my house or travel.
Buying something popular and "modern" to save some trees. I was supprised that this device will be jelaus when I'm leav it for a while to hole paper in my hands.

# I lost all of my e-books

After black and white graphics disaper on my device I saw something that I didnt want to see.

_My library is empty?!_

Yeah. It is. Quickly go to web and ask... Since then t was obvious. This is very well known issue with Kindle. You can google it by yourself because I don't want to get there back.

What I knew is that I'm from tech and I had few nice books in my hands some years ago so there is a chance that we can work it out.

# First 4 seconds are crucial

Crucial to not panic. Nothing else.
But still important is to not act with the device.
Best it to turn airplane mode and sing a song about some summer love.

Then connect and backup.

By backup (because I'm sitting on linux now) i mean that I need to save a state of it somehow.
I connect it to my laptop and check what kind of decidec I got mounted.

```
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS,MODEL
```

and I saw this!

```
sdb         vfat     /run/media/marcin/Kindle
```

Which was very good. There was not time to think more than copy whole device.
At this point there is no sens to wait or analyze. Copy needs to be done as fast as possible.

So:

```
sudo dd if=/dev/sdb of="kindle.img" bs=4M status=progress
```

Easiest and safest.
Now I had my stated. Locked.
Since now there is nothing more that could broke. Start for experimenting.

# Hunt for books

I knew what I was loogin for. After quick research in web I knew that teher are two types of files and I knew their headers.

Firs shot was for mobi. Why mobi? because epub is zip archive. Mobi is more unique and I thought that this will be easier to find.

So:

```
LC_ALL=C grep -aob 'BOOKMOBI' kindle.img
```

Yeah! Oldschool. But I had to check if I can find anything here. And I found!

```
189001788:BOOKMOBI
```

Multiple of them. To exaplain what you see is a part of *.mobi file type signifier and offset from the begining of my export.
I knew that searching for this didn't give me any proof that I got files to read.
This was a sign that its worth to go forward.

Next what was interesing me is what disk format I'm working with.
Easiest as I could:

```
file kindle.img
```

to see:

```
kindle.img: DOS/MBR boot sector, code offset 0x58+2, OEM-ID "mkdosfs", sectors/cluster 16, reserved sectors 4580, Media descriptor 0xf8, sectors/track 32, heads 64, sectors 13090718 (volumes > 32 MB), FAT (32 bit), sectors/FAT 6386, reserved 0x1, serial number 0x386d438c, label: "Kindle     "
```

Two more things was done at this point:

```
fdisk - l kindle.img
blkid -p kindle.img
```
