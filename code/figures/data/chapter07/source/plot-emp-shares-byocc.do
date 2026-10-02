#delimit ;
set more 1;

capture log close;
pause on;

/*
   Plot employment shares by occupation, by gender for 1960-2008
*/

log using plot-emp-shares-byocc.log, text replace;

tempfile data temp;

/********************/
/*   By Gender      */
/********************/

use census-cells-occ10-demog-1960-2008.dta, clear;

/* Drop agriculture */
drop if occ10==40;

/* Create 4 occupations from the current 10 */
gen occ4=1 if occ10==11 | occ10==12 | occ10==13;
replace occ4=2 if occ10==21 | occ10==22;
replace occ4=3 if occ10==23 | occ10==31;
replace occ4=4 if occ10==32 | occ10==33 | occ10==34;

label define occ4 1 "Professional, Managerial, Technical" 2 "Clerical, Sales" 3 "Production, Operators" 4 "Service";
label val occ4 occ4;

save `data', replace;

/* Collapse into occ cells */

collapse (rawsum) emp , by(year occ4);

/* Calculate employment share */
bys year: egen tot_emp=total(emp);
gen sh_emp=emp/tot_emp;

drop emp tot_emp;

/* Reshape */

reshape wide sh_emp, i(year) j(occ4);

label var sh_emp1 "Professional, Managerial, Technical";
label var sh_emp2 "Clerical, Sales";
label var sh_emp3 "Production, Operators";
label var sh_emp4 "Service";

/* Earnings year */
replace year=year-1;

/* Plot */

twoway connected sh_emp* year,  xlabel(1959(10)1999 2007) xtitle("Year") ytitle("Employement Share") title("Employment Shares by Major Occupation Groups, 1959-2007:" "Males and Females", size(medium)) ylabel(0(0.1)0.4) msymbol(O S T D) ytick(0(0.05)0.4, grid) saving(fig13a-census-emp-shares-mf.gph, replace);


/* Collapse into gender-occ cells */

use `data', clear;
collapse (rawsum) emp , by(year female occ4);

/* Calculate employment share */
bys year female: egen tot_emp=total(emp);
gen sh_emp=emp/tot_emp;

drop emp tot_emp;

/* Reshape */

reshape wide sh_emp, i(year female) j(occ4);

label var sh_emp1 "Professional, Managerial, Technical";
label var sh_emp2 "Clerical, Sales";
label var sh_emp3 "Production, Operators";
label var sh_emp4 "Service";

/* Earnings year */
replace year=year-1;

/* Plot */

twoway connected sh_emp* year if female==0, xlabel(1959(10)1999 2007) xtitle("Year") ytitle("Employement Share") title("Employment Shares by Major Occupation Groups, 1959-2007:"  "Males", size(medium)) ylabel(0(0.1)0.55) ytick(0(0.05)0.55, grid) msymbol(O S T D) saving(fig13b-census-emp-shares-m.gph, replace);

twoway connected sh_emp* year if female==1, xlabel(1959(10)1999 2007) xtitle("Year") ytitle("Employement Share") title("Employment Shares by Major Occupation Groups, 1959-2007:" "Females", size(medium)) ylabel(0(0.1)0.55) ytick(0(0.05)0.55, grid) msymbol(O S T D) saving(fig13c-census-emp-shares-f.gph, replace);


/********************/
/*   By Education  */
/********************/

use census-cells-occ10-demog-1960-2008.dta, clear;

/* Drop agriculture */
drop if occ10==40;

    /* Create 4 occupations from the current 10 */
gen occ4=1 if occ10==11 | occ10==12 | occ10==13;
replace occ4=2 if occ10==21 | occ10==22;
replace occ4=3 if occ10==23 | occ10==31;
replace occ4=4 if occ10==32 | occ10==33 | occ10==34;

label define occ4 1 "Professional, Managerial, Technical" 2 "Clerical, Sales" 3 "Production, Operators" 4 "Service";
label val occ4 occ4;

/* Collapse into educ-gender-occ cells */

* Combine CLG and GTC;
replace edcat5=4 if edcat5==5;
label define edcat5 4 "CLG+", modify;

collapse (rawsum) emp , by(year female edcat5 occ4);

/* Calculate employment share */
bys year female edcat5: egen tot_emp=total(emp);
gen sh_emp=emp/tot_emp;

drop emp tot_emp;

/* Reshape */
rename sh_emp sh_emp_;

reshape wide sh_emp_, i(year edcat5 occ4) j(female);

rename sh_emp_0 sh_emp_m_ed;
rename sh_emp_1 sh_emp_f_ed;

reshape wide sh_emp_*, i(year occ4) j(edcat5);

foreach i in m f
{;
    label var sh_emp_`i'_ed1 "HSD";
    label var sh_emp_`i'_ed2 "HSG";
    label var sh_emp_`i'_ed3 "SMC";
    label var sh_emp_`i'_ed4 "CLG+";
};

save `temp', replace;

/* Normalize to zero in 1959 */
sort year occ4;
foreach i in m f
{;        
    forval x=1/4
    {;
        local temp1=sh_emp_`i'_ed`x'[1];
        local temp2=sh_emp_`i'_ed`x'[2];
        local temp3=sh_emp_`i'_ed`x'[3];
        local temp4=sh_emp_`i'_ed`x'[4];
    
        
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'-`temp1' if occ==1;
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'-`temp2' if occ==2;
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'-`temp3' if occ==3;
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'-`temp4' if occ==4;
    };
};

/* Earnings year */
replace year=year-1;

label val occ4 occ4;

/* Plot */


* Males;
 
twoway connected sh_emp_m_* year if occ==1, xlabel(1959(10)1999 2007) ylabel(-0.2(.05).05) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ1.gph, replace) title("Professional, Managerial, Technical", size(medlarge)) ;

twoway connected sh_emp_m_* year if occ==2, xlabel(1959(10)1999 2007) ylabel(-0.2(.05).05) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ2.gph, replace) legend(off) title("Clerical, Sales", size(medlarge));

twoway connected sh_emp_m_* year if occ==3, xlabel(1959(10)1999 2007) ylabel(-0.15(.05).1) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ3.gph, replace) legend(off) title("Production, Operators", size(medlarge));

twoway connected sh_emp_m_* year if occ==4, xlabel(1959(10)1999 2007) ylabel(-0.05(.05).2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ4.gph, replace) legend(off) title("Service", size(medlarge));
    
    grc1leg census-emp-shares-byed-m-occ1.gph census-emp-shares-byed-m-occ2.gph census-emp-shares-byed-m-occ3.gph census-emp-shares-byed-m-occ4.gph, saving(fig14a-census-emp-shares-byed-m.gph, replace) title("Changes in Employment Shares 1959 to 2007 in Major Occupations" "by Educational Category: Males", size(medium)) legendfrom(census-emp-shares-byed-m-occ1.gph) scheme(s2mono);

    
* Females;
 
twoway connected sh_emp_f_* year if occ==1, xlabel(1959(10)1999 2007) ylabel(-0.15(.05).1) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ1.gph, replace) title("Professional, Managerial, Technical", size(medlarge)) ;

twoway connected sh_emp_f_* year if occ==2, xlabel(1959(10)1999 2007) ylabel(-0.2(.05).05) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ2.gph, replace) legend(off) title("Clerical, Sales", size(medlarge));

twoway connected sh_emp_f_* year if occ==3, xlabel(1959(10)1999 2007) ylabel(-0.15(.05).1) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ3.gph, replace) legend(off) title("Production, Operators", size(medlarge));

twoway connected sh_emp_f_* year if occ==4, xlabel(1959(10)1999 2007) ylabel(-0.05(.05).2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ4.gph, replace) legend(off) title("Service", size(medlarge));
    
    grc1leg census-emp-shares-byed-f-occ1.gph census-emp-shares-byed-f-occ2.gph census-emp-shares-byed-f-occ3.gph census-emp-shares-byed-f-occ4.gph, saving(fig14b-census-emp-shares-byed-f.gph, replace) title("Changes in Employment Shares 1959 to 2007 in Major Occupations" "by Educational Category: Females", size(medium)) legendfrom(census-emp-shares-byed-f-occ1.gph) scheme(s2mono) ;

/* NOT USED     
 /* Plot ratio */
 
 use `temp', clear;
 
 /* Compute ratio of employment relative to 1959 */
sort year occ4;
foreach i in m f
{;        
    forval x=1/4
    {;
        local temp1=sh_emp_`i'_ed`x'[1];
        local temp2=sh_emp_`i'_ed`x'[2];
        local temp3=sh_emp_`i'_ed`x'[3];
        local temp4=sh_emp_`i'_ed`x'[4];
    
        
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'/`temp1' if occ==1;
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'/`temp2' if occ==2;
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'/`temp3' if occ==3;
        replace sh_emp_`i'_ed`x'=sh_emp_`i'_ed`x'/`temp4' if occ==4;
    };
};


* Males;
 
twoway connected sh_emp_m_* year if occ==1, xlabel(1959(10)1999 2007) ylabel(0(.5)1.5) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ1.gph, replace) title("Professional, Managerial, Technical", size(medlarge)) ;

twoway connected sh_emp_m_* year if occ==2, xlabel(1959(10)1999 2007) ylabel(0(.5)1.5) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ2.gph, replace) legend(off) title("Clerical, Sales", size(medlarge));

twoway connected sh_emp_m_* year if occ==3, xlabel(1959(10)1999 2007) ylabel(0(.5)1.5) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ3.gph, replace) legend(off) title("Production, Operators", size(medlarge));

twoway connected sh_emp_m_* year if occ==4, xlabel(1959(10)1999 2007) ylabel(1(1)4) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-m-occ4.gph, replace) legend(off) title("Service", size(medlarge));
    
    grc1leg census-emp-shares-byed-m-occ1.gph census-emp-shares-byed-m-occ2.gph census-emp-shares-byed-m-occ3.gph census-emp-shares-byed-m-occ4.gph, saving(census-emp-shares-byed-ratio-m.gph, replace) title("Ratio of Employment Shares in Major Occupations to 1959 Level, 1959-2007" "by Educational Category: Males", size(medium)) legendfrom(census-emp-shares-byed-m-occ1.gph) scheme(s2mono);

    
* Females;
 
twoway connected sh_emp_f_* year if occ==1, xlabel(1959(10)1999 2007) ylabel(0.5(.5)2.5) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ1.gph, replace) title("Professional, Managerial, Technical", size(medlarge)) ;

twoway connected sh_emp_f_* year if occ==2, xlabel(1959(10)1999 2007) ylabel(0.5(.5)2.5) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ2.gph, replace) legend(off) title("Clerical, Sales", size(medlarge));

twoway connected sh_emp_f_* year if occ==3, xlabel(1959(10)1999 2007) ylabel(0.5(.5)2.5) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ3.gph, replace) legend(off) title("Production, Operators", size(medlarge));

twoway connected sh_emp_f_* year if occ==4, xlabel(1959(10)1999 2007) ylabel(1(1)3) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byed-f-occ4.gph, replace) legend(off) title("Service", size(medlarge));
    
    grc1leg census-emp-shares-byed-f-occ1.gph census-emp-shares-byed-f-occ2.gph census-emp-shares-byed-f-occ3.gph census-emp-shares-byed-f-occ4.gph, saving(census-emp-shares-byed-ratio-f.gph, replace) title("Ratio of Employment Shares in Major Occupations to 1959 Level, 1959-2007" "by Educational Category: Females", size(medium)) legendfrom(census-emp-shares-byed-f-occ1.gph) scheme(s2mono) ;


	
/*********************************/
/*   By Education: Style 2		*/
/*********************************/

use census-cells-occ10-demog-1960-2008.dta, clear;

/* Drop agriculture */
drop if occ10==40;

    /* Create 4 occupations from the current 10 */
gen occ4=1 if occ10==11 | occ10==12 | occ10==13;
replace occ4=2 if occ10==21 | occ10==22;
replace occ4=3 if occ10==23 | occ10==31;
replace occ4=4 if occ10==32 | occ10==33 | occ10==34;

label define occ4 1 "Professional, Managerial, Technical" 2 "Clerical, Sales" 3 "Production, Operators" 4 "Service";
label val occ4 occ4;

/* Collapse into educ-gender-occ cells */

* Combine CLG and GTC;
replace edcat5=4 if edcat5==5;
label define edcat5 4 "CLG+", modify;

collapse (rawsum) emp , by(year female edcat5 occ4);

/* Calculate employment share */
bys year female edcat5: egen tot_emp=total(emp);
gen sh_emp=emp/tot_emp;

drop emp tot_emp;

/* Reshape */
rename sh_emp sh_emp_;

reshape wide sh_emp_, i(year edcat5 occ4) j(female);

rename sh_emp_0 sh_emp_m_occ;
rename sh_emp_1 sh_emp_f_occ;

reshape wide sh_emp_*, i(year edcat5) j(occ4);

foreach i in m f
{;
    label var sh_emp_`i'_occ1 "Professional, Managerial, Technical";
    label var sh_emp_`i'_occ2 "Clerical, Sales";
    label var sh_emp_`i'_occ3 "Production, Operators";
    label var sh_emp_`i'_occ4 "Service";
};
	
/* Normalize to zero in 1959 */


sort year edcat5;
foreach i in m f
{;        
    forval x=1/4
    {;
        local temp1=sh_emp_`i'_occ`x'[1];
        local temp2=sh_emp_`i'_occ`x'[2];
        local temp3=sh_emp_`i'_occ`x'[3];
        local temp4=sh_emp_`i'_occ`x'[4];
    
        
        replace sh_emp_`i'_occ`x'=sh_emp_`i'_occ`x'-`temp1' if edcat5==1;
        replace sh_emp_`i'_occ`x'=sh_emp_`i'_occ`x'-`temp2' if edcat5==2;
        replace sh_emp_`i'_occ`x'=sh_emp_`i'_occ`x'-`temp3' if edcat5==3;
        replace sh_emp_`i'_occ`x'=sh_emp_`i'_occ`x'-`temp4' if edcat5==4;
    };
};
	
	
	
* Males;

twoway connected sh_emp_m_* year if edcat5==1, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-m-ed1.gph, replace) title("High School Drop Out", size(medlarge)) ;

twoway connected sh_emp_m_* year if edcat5==2, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-m-ed2.gph, replace) legend(off) title("High School Graduate", size(medlarge));

twoway connected sh_emp_m_* year if edcat5==3, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-m-ed3.gph, replace) legend(off) title("Some College Education", size(medlarge));

twoway connected sh_emp_m_* year if edcat5==4, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-m-ed4.gph, replace) legend(off) title("College Degree or Greater", size(medlarge));
    
    grc1leg census-emp-shares-byocc-m-ed1.gph census-emp-shares-byocc-m-ed2.gph census-emp-shares-byocc-m-ed3.gph census-emp-shares-byocc-m-ed4.gph, saving(census-emp-shares-byocc-m.gph, replace) title("Changes in Employment Shares 1959 to 2007 in Major Occupations" "by Educational Category: Males", size(medium)) legendfrom(census-emp-shares-byocc-m-ed1.gph) scheme(s2mono);


    
* Females;
 
twoway connected sh_emp_f_* year if edcat5==1, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-f-ed1.gph, replace) title("High School Drop Out", size(medlarge)) ;

twoway connected sh_emp_f_* year if edcat5==2, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-f-ed2.gph, replace) legend(off) title("High School Graduate", size(medlarge));

twoway connected sh_emp_f_* year if edcat5==3, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-f-ed3.gph, replace) legend(off) title("Some College Education", size(medlarge));

twoway connected sh_emp_f_* year if edcat5==4, xlabel(1959(10)1999 2007) ylabel(-0.1(.1)0.2) xtitle("Year") ytitle("Employement Share") saving(census-emp-shares-byocc-f-ed4.gph, replace) legend(off) title("College Degree or Greater", size(medlarge));
    
    grc1leg census-emp-shares-byocc-f-ed1.gph census-emp-shares-byocc-f-ed2.gph census-emp-shares-byocc-f-ed3.gph census-emp-shares-byocc-f-ed4.gph, saving(census-emp-shares-byocc-f.gph, replace) title("Changes in Employment Shares 1959 to 2007 in Major Occupations" "by Educational Category: Females", size(medium)) legendfrom(census-emp-shares-byocc-f-ed1.gph) scheme(s2mono);

*/
		
