


function DataAccess(){
	this.conection = "ra";
	this.valorborrar = 0;

	this.bbdd = TAFFY(jsonData);
}
DataAccess.prototype.getVulnerabilities = function(index, offset, target, vulnerability, criticality) {
	var bd = this.bbdd();
	if(target){
		bd = bd.filter({'target':target});
	}
	if(vulnerability){
		bd = bd.filter({'vulnerability':vulnerability});
	}
	if(criticality){
		bd = bd.filter({'criticality':parseInt(criticality)});
	}
	return bd.start((index*offset)+1).limit(offset).get();
	
};
DataAccess.prototype.getVulnerabilitiesCount = function(target, vulnerability, criticality) {
	var bd = this.bbdd();
	if(target){
		bd = bd.filter({'target':target});
	}
	if(vulnerability){
		bd = bd.filter({'vulnerability':vulnerability});
	}
	if(criticality){
		bd = bd.filter({'criticality':parseInt(criticality)});
	}
	return bd.count();
	
};
DataAccess.prototype.getTypeVulnerabilities = function() {
	return this.bbdd().distinct("vulnerability");
	
};
DataAccess.prototype.getTargets = function() {
	return this.bbdd().distinct("target");
	
};


