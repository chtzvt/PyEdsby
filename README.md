# PyEdsby

[Edsby](http://edsby.com/) doesn't have any sort of public API, so I did a little snooping to make a wrapper/library for it.

## Quickstart:
```python
import requests, json
from edsby import Edsby

edsby = Edsby(host='your_edsbyhost.edsby.com', username='your_username', password='your_password')
print json.dumps( edsby.getAllClassAverages() )
```

You can also check out more examples [here](https://github.com/ctrezevant/PyEdsby/tree/master/examples).

## Getting Started

Everything you need to know is explained comprehensively in the [Wiki](https://github.com/ctrezevant/PyEdsby/wiki). If you have any questions, feel free to [open an issue](https://github.com/ctrezevant/PyEdsby/issues/new) or [send me an email](https://www.ctis.me). Definitely check that documentation out first, though, because it's pretty extensive.

## Notes

First, let me apologize in advance for how convoluted the Edsby API is. I tried to abstract it all away as nicely as I could, but it's still a little crufty in places. With this library, however, it's much easier to work with. For this reason, I tried to keep the amount of processing done on the data returned minimal.

Secondly, I can only guarantee that this works with my school's own Edsby instance. I'm assuming they're all more or less the same, but I've only got one instance to test with. The endpoints seem nonspecific enough, but I can't rule out the possibility that you might still need to make some minor tweaks to fit your specific environment.

## App Ideas

PyEdsby implements more or less every major feature of the web interface, and then some. You can access all the important data visible on the web that you, as a student, would be interested in. Check out [the documentation](https://github.com/ctrezevant/PyEdsby/wiki/Methods) for a list of available methods.

Using PyEdsby, you could:
  - [Create a tool to find common classmates in each of your periods](https://github.com/ctrezevant/PyEdsby/blob/master/examples/commonClassmates.py),
  - Automatically crawl class feeds, and download attachments any time a teacher posts a new one,
  - Write a script that notifies you whenever your grades drop below a certain point,
  - Automatically post a message or link in the feed for a specific class,
  - Write a script that forwards Edsby direct messages to your phone,  
  - And so much more!

The only limits are your imagination, and whether or not Edsby is actually up and running (it goes down often). If you make something cool, let me know!

Best of luck, and enjoy! [Pull requests](https://github.com/ctrezevant/PyEdsby/pull/new/master) are always welcome:)

_The Edsby trademark and brand are property of CoreFour, Inc. This software is unofficial and not supported by CoreFour in any way. I do not work for CoreFour (nor would I ever want to)._
