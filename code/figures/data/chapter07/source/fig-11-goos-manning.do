use goos-manning-data.dta", clear

replace lo=lo/100
replace mid=mid/100
replace hi=hi/100

graph bar lo mid hi , over(n, label(angle(-90))) legend(label(1 "Lowest Paying 3rd") label(2 "Middle Paying 3rd") label(3 "Highest Paying 3rd")) title("Change in Employment Shares by Occupation 1993-2006 in 16 European Countries" "Occupations Grouped by Wage Tercile: Low, Middle, High", size(medsmall)) ytitle("Change in Employment Share", size(small)) ylabel(-0.15(0.05).2, grid) saving(goos-manning-fig.gph, replace)

