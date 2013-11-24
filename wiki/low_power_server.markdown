---
title: Low Power Server Build
bg-image: ../static/img/low_power.jpg
bg-img-src: https://drive.google.com/file/d/0B8hltkS8-lFqSG80bVZ4SnNlQjQ/edit?usp=sharing
---

My current homeserver is an ancient thing I've assembled out of hodgepodge
parts and pieces. Inspirted by [this post](http://www.codinghorror.com/blog/2013/09/the-2013-htpc-build.html)
by [Jeff Atwood](http://www.codinghorror.com/blog/2004/02/about-me.html) I
decided to see how much my current home server costs to run.

I pay for [PGE](http://www.portlandgeneral.com/default.aspx)'s 'clean energy'
program, which means I get energy only from renewable resources for an extra
0.03 or so cents a month. Not bad at all. Currenty kilowatt hours cost about
$0.1093 USD. Knowing this we compute the power draw of the current server per
day per month go get an approximate cost to run:

```
115 watts an hour (damn!)
115 * 24 = 2760 watts a day
2760 * 30 = 82,800 watt hours a month
82.8 * 0.1093 = $9.05 a month
```

$9.05 is a lot to pay for a single server to run 24/7. It's time for an upgrade.
So, taking Jeff's list I improved upon it slightly and added a new case. The
current ideal parts list:

* [Fractal Design's Node 304 Mini-ITX Case](http://www.newegg.com/Product/Product.aspx?Item=N82E16811352027)
* [ASRock Z87E-ITX Mini-ITX Motherboard](http://www.newegg.com/Product/Product.aspx?Item=N82E16813157374)
* [G.Skill Sniper Low Voltage Series 8GB Ram Kit](http://www.newegg.com/Product/Product.aspx?Item=N82E16820231461)
* [Dual-Core Haswell i3-4130T](http://www.newegg.com/Product/Product.aspx?Item=N82E16819116947)

I'm not sure how the low voltage ram will affect performance, but I am excited
to find out. Another notable addition is the upgraded motherboard, which has 6
sata ports as opposed to 4. The Node 304 has six drivebays, which is kind of
ridiculous for a mini-ITX case, but I have a need for at least four drivebays
([RAID 5](http://en.wikipedia.org/wiki/Standard_RAID_levels#RAID_5) is awesome).

All of this at full price costs around $450.96, plus shipping. That
makes the ROI for power usage (assuming Jeff's power usage is correct) pretty
terrible. Luckily, black friday/cyber monday is coming up and I'm hoping I can
knock $100-$200 of off the final price. We'll see.

