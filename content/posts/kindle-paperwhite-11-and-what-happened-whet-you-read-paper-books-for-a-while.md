---
title: I've lost my e-books
description: Kindle decide to move my stuff out. Is paper better than technology these
  days?
date: '2026-11-16'
image: /images/i-ve-lost-my-e-books-bcf08241-5d8e-4309-ad1b-d0f9cf0f7c77.png
tags:
- kindle-ai-recovery
draft: false
---

I thought that would be a good idea to have some of my books in one virtual place, i.e., when I'm waiting for something outside my house or traveling.
Buying something popular and "modern" to save some trees. I was surprised that this device would be jealous when I left it for a while to hold paper in my hands.

# I lost all of my e-books

After the black-and-white graphics disappeared on my device, I saw something I didn't want to see.

_My library is empty?!_

Yeah. It is. Quickly go to the web and ask... Since then, it was obvious. This is a very well-known issue with Kindle. You can Google it yourself because I don't want to get there back.

What I know is that I'm from tech, and I had a few nice books in my hands some years ago, so there is a chance that we can work it out.

# The first 4 seconds are crucial

Crucial to not panic. Nothing else.
But it is still important not to act with the device.
Best to turn on airplane mode and sing a song about some summer love.

Then connect and back up.

By backup (because I'm sitting on Linux now), I mean I need to save its state somehow.
I connect it to my laptop and check what kind of device I got mounted.

```
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS,MODEL
```

I saw this!

```
sdb         vfat     /run/media/marcin/Kindle
```

Which was very good. There was no time to think; I just copied the whole device. At this point, there is no sense in waiting or analyzing. Copy needs to be done as fast as possible.

So:

```
sudo dd if=/dev/sdb of="kindle.img" bs=4M status=progress
```

Easiest and safest.
Now I had my stated. Locked.
Since now there is nothing more that could break. Start experimenting.

# Hunt for books

I knew what I was looking for. After quick research on the web, I knew that there are two types of files, and I knew their headers.

The first shot was for MOBI. Why MOBI? Because EPUB is a ZIP archive. MOBI is more unique, and I thought that this would be easier to find.

So:

```
LC_ALL=C grep -aob 'BOOKMOBI' kindle.img
```

Yeah! Oldschool. But I had to check if I could find anything here. And I found!

```
189001788:BOOKMOBI
```

Multiple of them. To exaplain what you see is a part of *.mobi file type signifier and offset from the begining of my export.
I knew that searching for this didn't give me any proof that I got files to read.
This was a sign it was worth going forward.

Next, I wanted to know what disk file system I'm working with.
Easiest as I could:

```
file kindle.img
```

to see:

```
kindle.img: DOS/MBR boot sector, code offset 0x58+2, OEM-ID "mkdosfs", sectors/cluster 16, reserved sectors 4580, Media descriptor 0xf8, sectors/track 32, heads 64, sectors 13090718 (volumes > 32 MB), FAT (32 bit), sectors/FAT 6386, reserved 0x1, serial number 0x386d438c, label: "Kindle     "
```

Two more things were done at this point:

```
fdisk - l kindle.img
blkid -p kindle.img
```

After that, we had full visibility of where we are.

```
Disk kindle.img: 6,24 GiB, 6702472704 bytes, 13090767 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x00000000
```

```
kindle.img: LABEL_FATBOOT="Kindle" LABEL="Kindle" UUID="386D-438C" VERSION="FAT32" FSBLOCKSIZE="8192" BLOCK_SIZE="512" FSSIZE="6702447616" TYPE="vfat" USAGE="filesystem"
```

Here we need to stop. Because what I did next and what could be done are two separate things.

# Believe in "you"

In the past, I had the chance to read a great book: "Jak pisac wirusy" by Andrzej Dudek (How to write viruses). I don't think this book has been translated into English, but I believe there are many similar publications. A book from 1994 that I read when I was around 15 years old.

Madness. At that time, I was exploding with this new knowledge.

Today I'm grateful because of my understanding, i.e., how file systems work.

The next steps were simple, and after some time I successfully extracted 34 of 36 books. One of them lost its title page. Maybe not lost, but... hmmm... It no longer looks like a title page.

# Believe in your "AI mate"

After extracting, I was thinking about how much the modern world has moved forward. I usually don't touch this area of "IT", but...

I asked Codex, and in the first session, I brought only a disk dump and the information I'm looking for: EPUB and MOBI.

Would it surprise you if I said that after a few minutes I got most of what I recovered from Codex?

After a quick visual validation of the content and sharing my observations with Codex, I had to wait two more minutes to get the same result.

In addition to all of that, we've created a Python script.
Go here and try (if you need):
https://github.com/MarcinPetrow/kindle-recovery

Codex-like tools are very good at patterns, and we can not forget that they have access to knowledge about file systems, formats, and all of that.

# I didn't expect it

It's like Today we all got patterns. Younger generations got them less, so maybe this is why they're moving forward faster. Those patterns slow us down at some point. This was one of them.
I didn't think that this could be done this way, because in the past we did that differently.
The conclusion is simple: reset half of your mind and give yourself space to learn again.
This is the simplest advice, and it will probably be the hardest to implement.
