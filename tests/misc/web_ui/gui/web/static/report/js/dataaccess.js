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
	this.conection = "ra";
	this.valorborrar = 0;

	this.bbddVulnerabilities = TAFFY(vulnerabilitiesData);
	
}


DataAccess.prototype.getTargetTechnical = function() {
	var bd = this.bbddVulnerabilities();
	
	return bd.get();
	
};
DataAccess.prototype.getVulnerabilities = function(target, vulnerability, criticality, orderColumn, orderDirection) {
	var bd = this.bbddVulnerabilities();
	if(target){
		bd = bd.filter({'target':{'has':[target]}});
	}
	if(vulnerability){
		bd = bd.filter({'type':vulnerability});
	}
	if(criticality){
		bd = bd.filter({'criticality':parseInt(criticality)});
	}
	if(orderColumn){
		if(orderDirection=="asc")
		{
			orderDirection = ""
		}
		return bd.order(orderColumn +" " + orderDirection).get();
	}
	return bd.get();
	
};
DataAccess.prototype.getVulnerabilitiesCount = function(target, vulnerability, criticality) {
	var bd = this.bbddVulnerabilities();
	if(target){
		bd = bd.filter({'target':{'has':[target]}});
	}
	if(vulnerability){
		bd = bd.filter({'type':vulnerability});
	}
	if(criticality){
		bd = bd.filter({'criticality':parseInt(criticality)});
	}
	return bd.count();
	
};
DataAccess.prototype.getTypeVulnerabilities = function() {
	return this.bbddVulnerabilities().distinct("type");
	
};
DataAccess.prototype.getTargets = function() {
	var data= this.bbddVulnerabilities().distinct("target");
	var set = new jsSet();
	if(data){
		for(d in data){
			set.addAll(data[d]);
		}
	}
	return set.list();
};



