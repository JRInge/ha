IFTTT Notifications
===

`script.ifttt_notification` sends an alert message to the [If This Then That](http://ifttt.com/) service, containing up to three values.
This can then be called in an automation action like this:

    action:
    - service: script.ifttt_notification
      data:
        title: Alert title
        message: Message string
        url: Optional extra data

On IFTTT, an applet is set up so that *if* the Maker service webhook receives an event called `ha_alert` *then* it displays a rich message,
using the data above. The applet could use the url as either a link or an image, but can't easily do both due to the limitation of only
being able to pass three parameters.
