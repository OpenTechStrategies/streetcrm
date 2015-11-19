SWOPtact: a FOSS contact management system
==========================================

SWOPtact is a [free & open source software](LICENSE.md) contact
management system, meant especially for organizations that work with
large numbers of volunteer and semi-volunteer participants at
in-person meetings.

SWOPtact maintains a list of contacts with a history of their
attendance at events, which makes it also a list of events over time.
You can use SWOPtact to keep track of the people your organization
comes into contact with over time, and see how their engagement with
your mission grows, and to generate reports.

# Overview

_TODO (2015-11-19): documentation in progress_

SWOPtact tracks three basic types of entity: **Participants**,
**Institutions**, and **Events**.  (There are also _Tags_, an
admin-controlled namespace of labels that can be applied to the above
entities.

When you log in to SWOPtact, you log in as a user with one of the following three access levels:

* **Leader** Leaders are usually field organizers -- people who
  organize meetings, and who report back about the attendance and
  results of those meetings.  Leaders can create Participants,
  Institutions, and Events.  _(TBD: discuss how to use the sign-in
  sheet interface for maximum efficiency.)_

* **Staff** A Staff user can do everything a Leader can do, plus the
  following: Staff can also view & apply "leadership stages", which
  are used for internal tracking for Leadership development; these are
  internal-only -- Leaders themselves don't see those stages.  Staff
  can create and apply tags, and Staff can also archive entities.  (In
  general SWOPtact archives rather than deletes things, so that even
  very old information can still be retrieved later.)

* **Admin** can do everything above, plus create users.

See the [HOWTO](docs/HOWTO.md) guide for task-oriented documentation. 

# Installation

See [INSTALL.md](INSTALL.md).
