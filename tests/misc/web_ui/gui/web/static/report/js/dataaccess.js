function jsSet() {

    this.isNullAdded = false;

    var map = {};
	this.contains = function(key) {

        if (key === null)
            return this.isNullAdded;
        else if (key === undefined)
            return false;
        else
            return map[key] ? true : false;
    };

    this.add = function(val) {

        if (val === null)
            this.isNullAdded = true;
        else if (val !== undefined)
            map[val] = true;
        return this;
    };

    this.addAll = function(val) {

        if (val !== null && val !== undefined && val instanceof Array) {
            for ( var idx = 0; idx < val.length; idx++) {
                this.add(val[idx]);
            }
        }
        return this;
    };


    //  returns the number of elements in the set
    this.size = function() {

        return this.list().length;
    };

   
    this.list = function() {
        var arr = [];

        if (this.isNullAdded)
            arr.push(null);

        for (o in map) {
            // protect from inherited properties such as
            //  Object.prototype.test = 'inherited property';
            if (map.hasOwnProperty(o))
                arr.push(o);
        }
        return arr;
    };
};


function DataAccess(){
	var vulnerabilitiesArray = new Array();

	var targetsMap = new Array();
	$.each(data.resources, function(key, val){
		
		targetsMap[key] = val;
	});
	this.targetMap = targetsMap;
	this.bbddVulnerabilitiesSimple = TAFFY(data.vulnerabilities);
	this.bbddInformations = TAFFY(data.informations);
	this.auditScope = data.audit_scope;
}

DataAccess.prototype.getTargetTechnical = function(){
	return data.vulnerabilities;
}
DataAccess.prototype.getAuditScope = function(){
	var targetsScope = new Array();
	if(this.auditScope.domains){
		$.each(this.auditScope.domains, function(key, value){
			targetsScope.push(value);
		});
	}
	if(this.auditScope.web_pages){
		$.each(this.auditScope.web_pages, function(key, value){
			targetsScope.push(value);
		});
	}
	if(this.auditScope.addresses){
		$.each(this.auditScope.addresses, function(key, value){
			targetsScope.push(value);
		});
	}
	if(this.auditScope.roots){
		$.each(this.auditScope.roots, function(key, value){
			targetsScope.push(value);
		});
	}
	return targetsScope;
}

DataAccess.prototype.getTargetById = function(id){
	var d = this.targetMap["id_"+id];
	switch(d.data_subtype){
		case 2: return d.url;
		case 4: return d.hostname;
		case 5:
		case 6:
			return d.address;
	}
	return "";
}

DataAccess.prototype.getVulnerabilities = function(target, vulnerability, level, orderColumn, orderDirection) {
	var bd = this.bbddVulnerabilitiesSimple();
	if(target){
		bd = bd.filter({'domain_id':target});
	}
	if(vulnerability){
		bd = bd.filter({'display_name':vulnerability});
	}
	if(level){
		bd = bd.filter({'level':level});
	}
	if(orderColumn){
		if(orderDirection=="asc")
		{
			orderDirection = ""
		}
		return bd.order(orderColumn +" " + orderDirection).get();
	}else{
		return bd.order("level logicaldesc").get();
	}
	
	
};
DataAccess.prototype.getVulnerabilitiesCount = function(target, vulnerability, level) {
	var bd = this.bbddVulnerabilitiesSimple();
	if(target){
		bd = bd.filter({'domain_id':target});
	}
	if(vulnerability){
		bd = bd.filter({'display_name':vulnerability});
	}
	if(level){
		bd = bd.filter({'level':level});
	}
	return bd.count();
	
};
DataAccess.prototype.getTypeVulnerabilities = function() {
	return this.bbddVulnerabilitiesSimple().distinct("display_name");
	
};
DataAccess.prototype.getTargets = function() {
	return this.bbddVulnerabilitiesSimple().distinct("domain_id");
	
};



