


function DataAccess(){
	this.conection = "ra";
	this.valorborrar = 0;

	this.bbddVulnerabilities = TAFFY(vulnerabilitiesData);
	this.bbddTechnical = TAFFY(tecnicalData);
}
DataAccess.prototype.getVulnerabilities = function(index, offset, target, vulnerability, criticality) {
	var bd = this.bbddVulnerabilities();
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
	var bd = this.bbddVulnerabilities();
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
	return this.bbddVulnerabilities().distinct("vulnerability");
	
};
DataAccess.prototype.getTargets = function() {
	return this.bbddVulnerabilities().distinct("target");
	
};
DataAccess.prototype.getTargetTechnical = function(){
	return this.bbddTechnical().order("target").distinct("target");
}
DataAccess.prototype.getResourcesTechnical = function(target){
	var data= this.bbddTechnical().filter({'target':target}).distinct("resource");
	return TAFFY(data[0])().order("type").distinct("type");
}
DataAccess.prototype.getVulnerabilitiesTechnical = function(target, type){
	var data= this.bbddTechnical().filter({'target':target}).distinct("resource");
	var vuln =  TAFFY(data[0])().filter({'type':type}).distinct("vulnerabilities");
	return TAFFY(vuln[0])().order("type").get();
}
DataAccess.prototype.getDataVulnerabilityTechnical = function(target, type, id){
	var data= this.bbddTechnical().filter({'target':target}).distinct("resource");
	var vuln =  TAFFY(data[0])().filter({'type':type}).distinct("vulnerabilities");
	return TAFFY(vuln[0])().filter({"id":id}).get();
}

