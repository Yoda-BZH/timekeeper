# TimeKeeper

Timekeeper is a time-tracking tool.

It uses Redmine to store all entries.

It can display others sources of time-tracking tools, such as :
* OTRS
* Exchange
* Gitlab

Some limitations may apply for some sources.

For example, gitlab doesn't store the time when a time-entry has been submitted,
only the date.
Otrs, on the other hand, stores date and time.

All entries are display in a visual calendar.

Some time-entries can be converted in Redmine time-entries, such as Exchange / 
Office365 calendar entries.

## Authentication

Is uses Ldap/Active Directory to identify a user.

Once authenticated, the browser automatically sends the credentials for the
appropriate requests.
Those credentials are then sent to different API to fetch time-entries in 
third-party applications such as Redmine, or Metabase.

Credentials (user and password) are NOT stored by TimeKeeper IN ANY WAY.

The user's browser does.

## Tools used to build this application

* [Symfony](https://symfony.com/)
* [Fullcalendar](https://fullcalendar.io/)
* [JQuery](https://jquery.com/)
* [JQuery-UI](https://jqueryui.com/)
* [bootstrap](https://getbootstrap.com/)
* [Some bootstrap themes on bootswatch](https://www.bootstrapcdn.com/bootswatch/)
* [Python exchangelib (to connect to exchange/owa/office365 calendars)](https://pypi.org/project/exchangelib/)
* [memcached](https://memcached.org/) for storing data in cache
* [spectrum](http://bgrins.github.io/spectrum) for the `<input type="color">` polyfill for internet explorer

## Time entries cache

As much as possible, time entries are store in cache (memcached).

Things like redmine subjects, etc, are in cache.

Only the cache is used for the autocomplete feature.

The more the cache is filled, the less third-party sources are requested.

## Special features

Exchange events can be converted to redmine events, such as meetings.
Once converted, the exchange event is hidden.

Redmine issue IDs and subjects are proposed in the autocompleter.

Redmine entries can be resized or moved over the week after their creation.

## Requirements

* php7.4
* memcached
* php-memcached
* python3, python3-oauthlib, python3-requests-oauthlib

## Installation

After getting the source, run :
```
composer install
bin/console cache:clear --env=prod
```

## FAQ

* Can I access someone else's calendar ?
No.

* Can I use another login for another time-tracking source ?
No.

* Does it stores passwords somewhere ?
NO !

* How are event refreshed ?
A timed event in the user's browser fire an ajax call, which triggers an update
for that specific user.

If a user is not connected, events are not refreshed.

* Can the application refreshes itself the third-party sources ?
As it uses the users password, no.

* Can you make be able to do so ?
I would need to store the user's password, so no.

* How are redmine issues copied in cache ?
When a user is refreshing it's time entries, a request is made on redmine.

All issues where the user is affected to or is watcher of are queried.
This data is then stored in cache.

A lot of data cache is shared among users (redmine issues subjects, for example).

* Redmine (as gitlab) doesn't store the time of a time entry. How does time-keeper do it ?
Time-entries can have a comment. A special "tag" is append to the comment `TK: [start date - end date]`

Users commentes are kept, the tag is added afterward.

* Is timekeeper compatible with already existing time-entries in an existing redmine ?
Yes.

If the `TK` tag is not present, all events are stacked, starting at 08:00.

If the user chooses to rearrange them, the `TK` tag is then added (comments are still kept)

* Can I use another third-party source ?
If you have a mean to query it, sure, yes !

If need to implemets App\Services\Connectors\ConnectorInterface, and may extends
from \App\Services\Connectors\AbstractConnector

Entries are returned with this format:
```php
return array(
  array(
    'title' => 'Entry title',
    'start' => a datetime (using the iso-8601 format) when the entry begins,
    'end'   => a datetime (using the iso-8601 format) when the entry ends,
    'type'  => 'your plugin name',
    ),
  array(
    'title' => 'Another Entry title',
    'start' => a datetime (using the iso-8601 format) when the entry begins,
    'end'   => a datetime (using the iso-8601 format) when the entry ends,
    'type'  => 'your plugin name',
    ),
  ),
);
```
* What is metabase ?

It is a BI tool.
See [https://www.metabase.com/](https://www.metabase.com/) or 
[https://github.com/metabase/metabase](https://github.com/metabase/metabase)

* Why do you use it ?
Some third-party tool doesn't have an API.

Metabases is configured to query those third-parties, generates tables with all
the infos needed.

Metabase queries are then made, and requested with a nicer API using json.

* Why doesn't redmine uses metabase then ?
Fresh data is needed, especially when a Redmine time-entry is created.

There may be some delay before a time-entry appears in Metabase.

* Where did you get the idea of such tool ?
In a previous job, [NikTux](https://github.com/Niktux) made another similar tool
(redmine-unleashed), but far less visual.

I wanted an interface similar to Google Calendar, easy to used, pluggable with
several sources.

* Why this tool ?
Often, companies tracks spent time in redmine. But, for users, tracking time in
several redmine issues is a very long process.

This ease the process.
