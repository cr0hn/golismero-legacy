# How to use OpenVAS correlation

To use OpenVAS correlation you must setup plugins first. Follow these steps:

## 1 - Download OpenVAS plugins

You need the OpenVAS plugins feed. You can download it from [http://www.openvas.org/openvas-nvt-feed-current.tar.bz2](http://www.openvas.org/openvas-nvt-feed-current.tar.bz2) or get it from your OpenVAS installation.

## 2 - Generate database

Now we need to generate the database. To do that, you must run:

```python setup.py -p YOUR_PLUGIN_LOCATION -v```

## 3 - Done

Now we a pickled database called: **openvas.db**

# How to it works?

OpenVAS generator has a rules files. This files contains the expressions to find and correlate OpenVAS plugins with GoLismero data model.

The setup.py will find in their directory and load all files called "rules_*json", that contains rules.

# Available types of vulns

Each vulnerability has their type, to be easily to classified by te OpenVAS plugin. Available types are:

 * platform
 * software
 * webapp
 * malware
 * http

# Rules format

## Rules file format

Rules has he following format, as json:

 * comment: A comment about the rule.
 * rule_id: Unique identification of rule.
 * rule_type: Category of rule (list of rules listed above).
 * matching_types: Classes types, in GoLismero data model, that matches with this rule.
 * filename_rules: rules applied to the file name only.
 * content_rules: rules applied to the file content only.

## Rules detailed

Each rule (in section filename_rules and content_rules) has this format:

### Basic format:

 * Each section is formed by rules group and can has more than one rule group.
 * Each group can has more han one rule.

### Rule specification:

Each rule has 3 parameters: 

 * regex: String. This is the main information in rule. Can be referred to:
   * Regular expression: Rule will math if the this regex match.
   * Reference: If reference specified, rule matches if matches with all "rules_types" or concrete "rule_id". References starts with string: "REF://".
 * group: Integer or "\*". A regex can has more than one group. Rule matches if regex has this number of groups. If "\*" specified, all number of group matches.
 * operator: Boolean operator. Specify relation with the next rule (in rule group). Allowed operators are:
   * or: If this rule match, rule accepted. If not, it try to match with next rule. Default value if not specified.
   * and: Although it match, It try to match with next rule. If not match, rule is not accepted.
 * negate: boolean type. Rule is accepted the negation of rule matches.

