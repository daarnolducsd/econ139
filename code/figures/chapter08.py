"""Render the reviewed Chapter 8 figures, preserving two selected originals.

Eleven imported plots are approximate visual reconstructions. The two robot
bubble plots retain the original PNGs. Other colored lines,
confidence intervals, map categories and dense bubbles are traced as visible
silhouettes rather than inventing observations hidden by overlaps. Native axes,
legends and the seven dated timeline events are redrawn. No chapter is modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
SOURCE = BOOK / "images/08_images"
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "econ139-figure-cache/matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "econ139-figure-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import to_rgb, to_hex, to_rgba
from matplotlib.patches import Patch, PathPatch, Ellipse
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image
from scipy.ndimage import (gaussian_filter, minimum_filter, maximum_filter, zoom,
                           binary_closing, binary_fill_holes, distance_transform_edt,
                           label as component_labels, find_objects)
from figure_style import palette

plt.rcParams.update({"font.family": "Arial", "font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "econ139-chapter08", "lines.solid_capstyle": "round"})
P = palette()
RECORDS = []
PROOFS = False


def panel(unit, height=4.8, bottom=.20, right=.96):
    fig, ax = plt.subplots(figsize=(7.2, height))
    fig.subplots_adjust(left=.11, right=right, top=.86, bottom=bottom)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    for edge in ["left", "right", "top"]:
        ax.spines[edge].set_visible(False)
    ax.spines["bottom"].set_color(P["grid"])
    ax.grid(axis="y", color=P["grid"], lw=.65)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelcolor=P["muted"], pad=7)
    ax.text(0, 1.07, unit, transform=ax.transAxes, color=P["muted"], fontsize=10)
    return fig, ax


def pixels(name):
    return np.asarray(Image.open(SOURCE / name).convert("RGB"), dtype=float)


def near(rgb, color, tolerance=32):
    return np.linalg.norm(rgb - np.array(color), axis=2) < tolerance


def trace(ax, mask, extent, color, alpha=1, zorder=3, smooth=False):
    """Contour a binary visible-source mask into paths with native SVG geometry.

    This preserves visible silhouettes, including holes and overlapping bubbles.
    It does not identify countries, firms, demographic observations or estimates.
    No random sampling, statistical smoothing or extrapolation is performed.
    """
    if not np.any(mask):
        return 0
    h, w = mask.shape
    xmin, xmax, ymin, ymax = extent
    # Contours preserve pixel-center calibration; zero padding closes edge paths.
    if smooth:
        # Subpixel contour cleanup affects silhouette edges only, not centers,
        # the fitted relationship, or the statistical series.
        mask = gaussian_filter(zoom(mask.astype(float), 3, order=1), .7)
        h, w = mask.shape
    work = np.pad(mask.astype(float), 1)
    x = np.linspace(xmin - (xmax-xmin)/w/2, xmax + (xmax-xmin)/w/2, w+2)
    y = np.linspace(ymax + (ymax-ymin)/h/2, ymin - (ymax-ymin)/h/2, h+2)
    helper, temp = plt.subplots()
    contours = temp.contour(x, y, work, levels=[.5])
    paths = contours.get_paths()
    for path in paths:
        ax.add_patch(PathPatch(path, facecolor=color, edgecolor="none", alpha=alpha, zorder=zorder))
    plt.close(helper)
    return int(mask.sum())


def sampled_line(mask, extent, positions):
    """Read approximate line centers at fixed x positions from source colors.

    At crossings, short occlusions are joined by straight plot segments. This
    is a visual interpolation, not recovery of hidden monthly observations.
    """
    h,w=mask.shape; values=[]
    for x in positions:
        col=np.clip(int(round(x)),0,w-1)
        rows=np.where(mask[:,max(0,col-2):min(w,col+3)])[0]
        values.append(float(np.median(rows)) if len(rows) else np.nan)
    values=np.array(values)
    good=np.isfinite(values)
    assert good.sum()>=2, "Not enough visible source line to reconstruct"
    values=np.interp(positions,np.asarray(positions)[good],values[good],left=np.nan,right=np.nan)
    xmin,xmax,ymin,ymax=extent
    return xmin+np.asarray(positions)/w*(xmax-xmin), ymax-values/h*(ymax-ymin)


def native_fit(ax, mask, extent, color, lw=1.5, ls="-"):
    """Redraw a straight source fit with a uniform native SVG stroke."""
    yy,xx=np.where(mask)
    columns=np.unique(xx)
    centers=np.array([np.median(yy[xx==x]) for x in columns])
    slope,intercept=np.polyfit(columns,centers,1)
    ends=np.array([columns.min(),columns.max()])
    xmin,xmax,ymin,ymax=extent;h,w=mask.shape
    x=xmin+ends/w*(xmax-xmin);y=ymax-(intercept+slope*ends)/h*(ymax-ymin)
    ax.plot(x,y,color=color,lw=lw,ls=ls,zorder=5)


def native_bubbles(ax, mask, extent):
    """Approximate visible circle centers/radii; draw smooth native outlines.

    Isolated silhouettes use their centroid and area-equivalent radius. Touching
    circles use visible distance peaks; fully hidden bubbles are not inferred.
    The readings are graphical approximations, not industry observations.
    """
    mask=binary_fill_holes(binary_closing(mask,structure=np.ones((3,3))))
    components,_=component_labels(mask)
    circles=[]
    for index,box in enumerate(find_objects(components),1):
        if box is None:continue
        ys,xs=box;region=components[box]==index
        if region.sum()<4:continue
        distance=distance_transform_edt(np.pad(region,1))[1:-1,1:-1]
        peaks=(distance==maximum_filter(distance,size=5))&(distance>=1.3)
        groups,count=component_labels(peaks)
        if count<=1:
            cy,cx=np.mean(np.argwhere(region),axis=0)
            candidates=[(cx,cy,np.sqrt(region.sum()/np.pi))]
        else:
            candidates=[]
            for group in range(1,count+1):
                cy,cx=np.mean(np.argwhere(groups==group),axis=0)
                candidates.append((cx,cy,float(distance[groups==group].max())))
        retained=[]
        for cx,cy,radius in sorted(candidates,key=lambda p:-p[2]):
            if any(np.hypot(cx-x,cy-y)<.6*max(radius,r) for x,y,r in retained):continue
            retained.append((cx,cy,radius))
            circles.append((cx+xs.start,cy+ys.start,radius))
    xmin,xmax,ymin,ymax=extent;h,w=mask.shape
    for index,(cx,cy,radius) in enumerate(sorted(circles,key=lambda p:-p[2])):
        center=(xmin+cx/w*(xmax-xmin),ymax-cy/h*(ymax-ymin))
        bubble=Ellipse(center,2*radius/w*(xmax-xmin),2*radius/h*(ymax-ymin),
                       facecolor=to_rgba(P["primary"],.30),
                       edgecolor=to_rgba(P["primary"],.95),linewidth=.7,zorder=3)
        bubble.set_gid(f"labor-share-circle-{index+1}")
        ax.add_patch(bubble)
    return circles


def save(fig, stem, caption, originals, method, out, details=None):
    fig.savefig(out / f"{stem}.svg", transparent=True, metadata={"Date": None})
    if PROOFS:
        fig.patch.set_alpha(1)
        fig.savefig(out / f"{stem}.png", facecolor="white", dpi=150)
    plt.close(fig)
    RECORDS.append({"stem": stem, "caption": caption, "originals": originals,
                    "method": method, "details": details or {},
                    "source_sha256": {f: hashlib.sha256((SOURCE/f).read_bytes()).hexdigest() for f in originals}})


def growth(out):
    # The current image has 22 annual marker positions. Coordinates below are
    # read from that image, not a substitute current-vintage country series.
    a = pixels("robots2.png")
    fig, ax = panel("Robots per 1,000 workers in 1993", right=.69, height=4.9)
    years = np.arange(1993, 2015)
    points = {
        "Germany": [1.31,1.44,1.63,1.91,2.12,2.32,2.57,2.89,3.14,3.33,3.56,3.81,3.99,4.19,4.43,4.57,4.55,4.68,4.97,5.12,5.30,5.56],
        "Denmark, Finland, France,\nItaly and Sweden": [.60,.67,.74,.81,.88,.96,1.07,1.23,1.36,1.44,1.53,1.65,1.79,1.89,2.02,2.12,2.12,2.13,2.16,2.15,2.15,2.21],
        "United States": [.34,.39,.45,.48,.53,.57,.64,.71,.77,.81,.88,.97,1.10,1.19,1.27,1.32,1.30,1.36,1.45,1.56,1.70,1.86],
        "Norway, Spain and UK": [.28,.30,.32,.36,.40,.45,.50,.60,.71,.77,.82,.89,.96,1.04,1.10,1.13,1.12,1.11,1.14,1.13,1.11,1.13],
    }
    for (label, values), role, marker, ls in zip(points.items(), ["primary","third","comparison","fourth"], ["s","^","D","o"], ["-","--","-",":"]):
        ax.plot(years, values, color=P[role], marker=marker, ms=3.2, lw=1.8, ls=ls)
        ax.annotate(label, (2014, values[-1]), (8, 0), textcoords="offset points", va="center", color=P[role], fontsize=9.5)
    ax.set(xlim=(1992.5,2014.5), ylim=(0,5.9), xticks=[1993,2000,2007,2014], yticks=range(6))
    ax.set_xlabel("Year", color=P["muted"], labelpad=10)
    save(fig,"robot-growth","Growth in Industrial Robots",["robots2.png"],"Approximate annual marker digitization",out,{"years":years.tolist(),"series":points})


def robot_map(out):
    a = pixels("robots3.png")
    crop = a[48:481,40:799].copy()
    # Remove the old legend only; its swatches sit in the empty Atlantic area.
    crop[280:,658:] = 255
    levels = np.array([0,16,32,49,68,89,114,136,163,188,217])
    gray = crop.mean(axis=2)
    closest = np.argmin(abs(gray[:,:,None] - levels),axis=2)
    fig, ax = plt.subplots(figsize=(7.2,4.6))
    fig.subplots_adjust(left=.01,right=.79,bottom=.04,top=.94)
    ax.set_aspect("equal"); ax.set_axis_off()
    light = np.array(to_rgb("#F3EAE1")); dark = np.array(to_rgb(P["comparison"]))
    colors = [to_hex(dark*(1-i/10)+light*(i/10)) for i in range(11)]
    for i,color in enumerate(colors):
        trace(ax,(closest==i)&(gray<235),(0,759,0,433),color)
    ax.set(xlim=(0,759),ylim=(0,433))
    labels=["5.00–9.04","2.64–5.00","2.00–2.64","1.75–2.00","1.46–1.75","1.29–1.46","1.08–1.29","0.98–1.08","0.84–0.98","0.67–0.84","0.35–0.67"]
    fig.legend([Patch(facecolor=c) for c in colors],labels,loc="center right",bbox_to_anchor=(1,.48),frameon=False,fontsize=8.5,labelcolor=P["muted"],handlelength=1.1,handleheight=.9)
    fig.text(.81,.88,"Additional robots\nper 1,000 workers\n1993–2007",fontsize=9,color=P["muted"],va="top")
    save(fig,"robot-map","Exposure to Industrial Robots by Commuting Zone",["robots3.png"],"Approximate vector trace of the existing map",out,{"legend_intervals":labels,"limits":"Source boundaries and category silhouettes traced; no reconstructed geographic dataset. Anti-aliased boundary pixels are approximate."})


def retained_original(filename, stem, caption):
    selection=json.loads((HERE/"data/chapter08/selection.json").read_text())
    assert selection["retain_original"][stem]==filename
    RECORDS.append({"stem":stem,"caption":caption,"originals":[filename],
                    "method":"Retained original by user decision","selection":"original",
                    "selected_asset":f"images/08_images/{filename}",
                    "details":{"status":"Original retained; reconstruction superseded"},
                    "source_sha256":{filename:hashlib.sha256((SOURCE/filename).read_bytes()).hexdigest()}})


def colored_scatter(out, filename, stem, caption, crop, extent, xticks, yticks, unit, xlabel, multi=False):
    a = pixels(filename)
    x0,y0,x1,y1=crop; a=a[y0:y1,x0:x1].copy()
    fig, ax=panel(unit,height=6.12*(y1-y0)/(x1-x0)+2.0,bottom=.25 if multi else .20)
    ax.set_box_aspect((y1-y0)/(x1-x0))
    circles=[]
    if multi:
        # The original legend occupies blank space within the plotting region.
        a[0:150,510:] = 255
        targets=[(149,172,117),(188,125,128),(143,171,167),(85,119,158),(249,168,102)]
        roles=["education_dropout","education_highschool","education_somecollege","comparison","primary"]
        labels=["High-school dropout","High school","Some college","College","Postgraduate"]
        errors=[]; strengths=[]
        for target in targets:
            # Sources use translucent bubbles; hue direction identifies both
            # opaque outlines and pale fills without changing their positions.
            direction=255-np.array(target)
            delta=255-a
            ratio=(delta@direction)/(direction@direction)
            distance=np.linalg.norm(delta-ratio[:,:,None]*direction,axis=2)
            errors.append(distance); strengths.append(ratio)
        errors=np.stack(errors,axis=2)
        assigned=np.argmin(errors,axis=2)
        chromatic=a.max(axis=2)-a.min(axis=2)>6
        for i,role in enumerate(roles):
            trace(ax,(assigned==i)&(errors[:,:,i]<22)&(strengths[i]>.08)&chromatic,extent,P[role],alpha=.65,smooth=True)
        handles=[Line2D([],[],marker="o",ls="",color=P[r],label=l) for r,l in zip(roles,labels)]
        ax.legend(handles=handles,loc="upper center",bbox_to_anchor=(.5,-.23),ncol=3,frameon=False,fontsize=8.3,labelcolor=P["muted"])
        # The source red fitted line is retained independently of bubbles.
        native_fit(ax,(a[:,:,0]>180)&(a[:,:,1]<100)&(a[:,:,2]<100),extent,P["ink"])
    else:
        blue=(a[:,:,2]-a[:,:,0]>15)&(a[:,:,2]-a[:,:,1]>1)&(a[:,:,0]<240)
        circles=native_bubbles(ax,blue,extent)
        # Retype the existing industry labels instead of enlarging their pixel
        # outlines. The fitted line endpoints are approximate source readings.
        ax.plot([-6.0,8.5],[11.5,-40],color=P["ink"],lw=1.1,zorder=4)
        labels=[("Apparel",(-2.4,17.7),(-2.0,17.7)),
                ("Prof. services",(.2,-1),(.7,-2)),
                ("Restaurants",(-1.1,-8),(-4.1,-6.5)),
                ("Retail",(1.5,-17),(2.1,-21.5)),
                ("Plastics",(2.8,-16),(3.0,-12)),
                ("Comp. services",(4.8,-24),(5.0,-24.5)),
                ("Cars",(4.8,-38),(5.0,-37.5)),
                ("Metals",(8.5,-39),(8.7,-38.5)),
                ("Chemicals",(-.2,-47),(.1,-47.5))]
        for label,anchor,position in labels:
            ax.annotate(label,anchor,position,color=P["ink"],fontsize=9.5,va="center",
                        arrowprops={"arrowstyle":"-","lw":.5,"color":P["muted"]} if label in ["Restaurants","Retail","Plastics"] else None)
    ax.set(xlim=extent[:2],ylim=extent[2:],xticks=xticks,yticks=yticks)
    ax.set_yticklabels([f"{v:g}%" for v in yticks])
    if multi:ax.set_xticklabels([f"{v:g}%" for v in xticks])
    ax.set_xlabel(xlabel,color=P["muted"],labelpad=11)
    details={"source_crop_pixels":crop,"data_extent":extent,"limits":"Approximate source geometry and fitted line; no underlying industry or demographic data replication."}
    if not multi:
        details.update({"circle_centers_radii_crop_pixels":circles,"circle_outline_width_pt":.7,
                        "limits":"Visible source circles approximated by centroids/areas or distance peaks in touching silhouettes. Fully hidden circles are not inferred; no industry-data replication."})
    save(fig,stem,caption,[filename],"Approximate native circles with crisp outlines" if not multi else "Approximate colored bubble silhouettes",out,details)


def humlum(out):
    blue=(48,112,184); orange=(217,113,61)
    configs=[("humlum1.png","wage-bill","Firm Wage Bill Around Robot Adoption",[(87,87,556,448)],[-4,4],[-5,35],[None]),
             ("humlum2.png","sales","Sales Around Robot Adoption",[(111,69,581,431)],[-4,4],[-5,35],[None]),
             ("humlum3.png","skill-wage-bills","Employment by Skill Level Around Robot Adoption",[(151,170,620,531),(725,170,1194,531)],[-4,5],[-40,50],["Production workers","Tech workers"])]
    for filename,stem,caption,crops,xlim,ylim,titles in configs:
        a=pixels(filename)
        panels=[]
        if len(crops)==1:
            fig,ax=panel("Percent change",height=4.8); axes=[ax]
        else:
            # Vertical panels preserve readable text at the 680px book width.
            fig,axes=plt.subplots(2,1,figsize=(7.2,8.5))
            fig.subplots_adjust(left=.12,right=.96,top=.91,bottom=.10,hspace=.43)
            for ax in axes:
                for side in ["top","right","left"]:ax.spines[side].set_visible(False)
                ax.spines["bottom"].set_color(P["grid"]);ax.grid(axis="y",color=P["grid"],lw=.65);ax.set_axisbelow(True);ax.tick_params(length=0,labelcolor=P["muted"],pad=7)
                ax.text(0,1.05,"Percent change in wage bill",transform=ax.transAxes,color=P["muted"],fontsize=9.5)
        for i,(ax,crop,title) in enumerate(zip(axes,crops,titles)):
            x0,y0,x1,y1=crop; part=a[y0:y1,x0:x1+2].copy()
            # Existing legends lie in empty upper-left plot space.
            part[0:75,0:160]=255
            endx=4 if len(crops)==2 and i==1 else xlim[1]
            ext=(xlim[0],endx,ylim[0],ylim[1])
            years=np.arange(xlim[0],endx+1)
            source_x=np.linspace(0,x1-x0,len(years))
            _,data=sampled_line(near(part,blue,35),ext,source_x)
            data[years==-1]=0  # Original omitted/reference year.
            if stem=="wage-bill":model=[0,0,0,0,9.1,8.9,8.6,8.45,8.3]
            elif stem=="sales":model=[0,0,0,0,20.4,20,19.6,19,18.5]
            elif i==0:model=[0,0,0,0,-22.5,-22,-21.6,-21.1,-20.7,-20]
            else:model=[0,0,0,0,29.5,29,28.5,28,27.3]
            # Read the visible tops/bottoms of pointwise intervals. Redraw each
            # with the same weight and dash pattern, independently of the data
            # line. These are bars, not a continuous confidence band.
            blue_mask=(part[:,:,2]-part[:,:,0]>40)&(part[:,:,2]-part[:,:,1]>25)&(part[:,:,0]<220)
            intervals=[]
            for year,col in zip(years,source_x):
                col=int(round(col))
                rows=np.where(blue_mask[:,max(0,col-2):col+3])[0]
                if year==-1 or len(rows)==0 or rows.max()-rows.min()<8:continue
                low=ylim[1]-rows.max()/len(part)*(ylim[1]-ylim[0])
                high=ylim[1]-rows.min()/len(part)*(ylim[1]-ylim[0])
                ax.vlines(year,low,high,color=P["primary"],lw=.95,linestyles=(0,(5,4)),zorder=2)
                intervals.append([int(year),float(low),float(high)])
            ax.plot(years,data,color=P["primary"],lw=2,zorder=4)
            ax.plot(years,model,color=P["comparison"],lw=2,ls=(0,(6,4)),zorder=4)
            panels.append({"years":years.tolist(),"data":data.tolist(),"model":model,"intervals":intervals,"interval_linewidth_pt":.95,"interval_dash_pattern_pt":[5,4]})
            ax.axhline(0,color=P["muted"],lw=.6,zorder=1)
            ax.set(xlim=(ext[0]-.12,ext[1]+.12),ylim=ext[2:],xticks=range(-4,endx+1),yticks=range(ylim[0] if ylim[0]!=-5 else 0,ylim[1]+1,10 if len(crops)==2 else 5))
            ax.set_xlabel("Years relative to robot adoption",color=P["muted"],labelpad=10)
            if title:ax.set_title(title,loc="left",pad=30,color=P["ink"],fontsize=12,fontweight="bold")
            ax.legend(handles=[Line2D([],[],color=P["primary"],lw=2,label="Data"),Line2D([],[],color=P["comparison"],lw=2,ls="--",label="Model")],frameon=False,loc="upper left",fontsize=9,labelcolor=P["muted"])
        save(fig,stem,caption,[filename],"Approximate source digitization with uniform native lines and intervals",out,{"source_crop_pixels":crops,"panels":panels,"limits":"Visible pointwise interval endpoints read approximately from the source; confidence level is not inferred. Skill panels plot wage bills, although the existing caption says employment."})


def timeline(out):
    events=[("ChatGPT launch","2022-11-30"),("GPT-4 release","2023-03-14"),("Claude release","2023-03-14"),("Claude 2","2023-07-11"),("Gemini release","2023-12-06"),("Claude 3","2024-03-04"),("GPT-4o","2024-05-13")]
    fig,ax=plt.subplots(figsize=(7.2,4.8))
    fig.subplots_adjust(left=.32,right=.94,top=.94,bottom=.15)
    dates=[np.datetime64(d) for _,d in events]
    y=np.arange(7)[::-1]
    for i,(label,date) in enumerate(events):
        x=mdates.date2num(np.datetime64(date))
        ax.hlines(y[i],mdates.date2num(np.datetime64("2022-10-01")),x,color=P["grid"],lw=1)
        ax.plot(x,y[i],"o",ms=6,color=P["primary"] if i%2==0 else P["comparison"])
        ax.annotate(np.datetime64(date).astype(object).strftime("%d %b %Y").lstrip("0"),(x,y[i]),(9,0),textcoords="offset points",va="center",fontsize=9,color=P["muted"])
    ax.set_yticks(y,[v[0] for v in events],color=P["ink"])
    ax.set_xlim(np.datetime64("2022-10-01"),np.datetime64("2024-11-01"));ax.set_ylim(-.6,6.6)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,7]));ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    for spine in ax.spines.values():spine.set_visible(False)
    ax.tick_params(length=0,labelcolor=P["muted"],pad=9)
    ax.set_xlabel("Release date",color=P["muted"],labelpad=12)
    save(fig,"llm-timeline","Key Events in the Modern LLM Timeline",[],"Exact seven events and dates from the current Python cell",out,{"events":events,"limits":"Historical events in the chapter; no update to the event list."})


AGE_COLORS=[(56,118,176),(241,135,49),(80,157,62),(199,61,48),(141,107,184),(133,89,77)]
AGE_LABELS=["22–25","26–30","31–34","35–40","41–49","50+"]
AGE_BW=[("#000000",2.9,"-"),("#303030",2.35,"-"),
        ("#555555",1.9,(0,(6,2))),("#777777",1.55,(0,(2,2))),
        ("#999999",1.25,"-.") ,("#AAAAAA",1.05,(0,(5,2,1,2)))]


def age_chart(out, wages=False):
    filename="ai_4.png" if wages else "ai_1.png"
    a=pixels(filename)
    if wages:
        # Plot boundaries calibrated against the original 1798 × 1484 image.
        crops=[(151,95,871,514),(1015,95,1735,514),(151,724,871,1143),(1015,724,1735,1143)]
        titles=["Software developers","Marketing and sales managers","First-line production supervisors","Health aides"]
        fig,axes=plt.subplots(4,1,figsize=(7.2,15.5))
        fig.subplots_adjust(left=.11,right=.96,top=.95,bottom=.15,hspace=.57)
    else:
        crops=[(168,151,1043,804)];titles=[None]
        fig,ax=panel("Employment index · October 2022 = 1",height=5.8,bottom=.31)
        axes=[ax]
    t0=mdates.date2num(np.datetime64("2021-01-01"));t1=mdates.date2num(np.datetime64("2025-07-01"));cut=mdates.date2num(np.datetime64("2022-10-01"))
    series=[]
    for ax,crop,title in zip(axes,crops,titles):
        x0,y0,x1,y1=crop;part=a[y0:y1,x0:x1]
        # Source axes include padding around the first/last monthly point.
        # Calibration uses the 1.0 and 0.9 horizontal ticks and monthly endpoints.
        if wages:
            # At source width, data start 32px after the left spine and stop 32px
            # before the right spine. 1.0 is at y304/934, 0.9 at y388/1018.
            xleft=t0-(t1-t0)*32/656;xright=t1+(t1-t0)*32/656
            ext=(xleft,xright,.75,1.25)
        else:
            xleft=t0-(t1-t0)*39/797;xright=t1+(t1-t0)*39/797
            ext=(xleft,xright,.75,1.25)
        positions=np.linspace(32,688,55) if wages else np.linspace(39,836,55)
        for j in reversed(range(6)):
            x,y=sampled_line(near(part,AGE_COLORS[j],25),ext,positions)
            y[21]=1  # All source age indices share this normalization.
            color,weight,pattern=AGE_BW[j]
            ax.plot(x,y,color=color,lw=weight,ls=pattern,zorder=10-j)
            series.append({"panel":title,"age":AGE_LABELS[j],"x":x.tolist(),"y":y.tolist(),"linewidth_pt":weight,"color":color})
        if wages:
            for side in ["top","right","left"]:ax.spines[side].set_visible(False)
            ax.spines["bottom"].set_color(P["grid"]);ax.grid(axis="y",color=P["grid"],lw=.65);ax.set_axisbelow(True);ax.tick_params(length=0,labelcolor=P["muted"],pad=7)
            ax.set_title(title,loc="left",fontsize=12,color=P["ink"],fontweight="bold",pad=14)
        ax.axvline(cut,color=P["muted"],lw=1,ls="--")
        ax.axhline(1,color=P["muted"],lw=.6,zorder=1)
        ax.set(xlim=(xleft,xright),ylim=(.75,1.25),yticks=[.8,.9,1,1.1,1.2])
        ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_xlabel("Date",color=P["muted"],labelpad=10)
    handles=[Line2D([],[],color=c,lw=w,ls=s,label=l) for (c,w,s),l in zip(AGE_BW,AGE_LABELS)]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.52,.018 if wages else .055),ncol=3,frameon=False,title="Age group",fontsize=9.5,labelcolor=P["muted"])
    if wages:fig.text(.11,.985,"Wage index · October 2022 = 1",fontsize=10,color=P["muted"],va="top")
    else:axes[0].text(.02,.95,"Dashed line: October 2022",transform=axes[0].transAxes,fontsize=9,color=P["muted"])
    save(fig,"ai-wages" if wages else "ai-age-employment","Wages in Different Occupations by AI Exposure" if wages else "Software Developer Employment by Age",[filename],"Approximate native monochrome age lines",out,{"source_crop_pixels":crops,"series":series,"limits":"Current vintage retained. Approximate monthly readings; short source occlusions are joined linearly. Younger ages have progressively heavier/darker native strokes, with the same age mapping in employment and all four wage panels."})


def exposure(out, older=False):
    filename="ai_3.png" if older else "ai_2.png";a=pixels(filename)
    crop=(109,39,615,391) if older else (108,65,867,594)
    x0,y0,x1,y1=crop;part=a[y0:y1,x0:x1].copy()
    # The inset is below every plotted series; remove only its empty-area legend.
    if older:part[242:324,244:]=255
    else:part[368:477,370:]=255
    part[:3,:]=255;part[-3:,:]=255;part[:,:3]=255;part[:,-3:]=255
    fig,ax=panel("Employment index · October 2022 = 1",height=5.2,bottom=.25)
    t0=mdates.date2num(np.datetime64("2021-01-01"));t1=mdates.date2num(np.datetime64("2025-07-01"))
    leftpad=22 if older else 34; span=(x1-x0)-2*leftpad
    xleft=t0-(t1-t0)*leftpad/span;xright=t1+(t1-t0)*leftpad/span
    ext=(xleft,xright,.7,1.25)
    gray=part.mean(axis=2);achromatic=part.max(axis=2)-part.min(axis=2)<7
    # Recover approximate monthly line centers from the five original gray
    # levels. Reject pale anti-alias edges adjacent to a darker source core.
    reference_col=int(round((mdates.date2num(np.datetime64("2022-10-01"))-xleft)/(xright-xleft)*part.shape[1]))
    gray[:,reference_col-3:reference_col+4]=255
    core=minimum_filter(gray,size=(3,1))
    positions=np.linspace(leftpad,part.shape[1]-leftpad,55)
    styles=[("#B0B0B0",1.05),("#8A8A8A",1.35),("#606060",1.65),("#333333",2.1),("#000000",2.7)]
    series=[]
    for level,(color,weight) in zip([228,188,135,83,26],styles):
        mask=achromatic&(abs(gray-level)<(15 if older else 7))&(core>level-20)
        x,y=sampled_line(mask,ext,positions)
        y[21]=1
        ax.plot(x,y,color=color,lw=weight,zorder=3+len(series))
        series.append({"source_gray":level,"x":x.tolist(),"y":y.tolist(),"color":color,"linewidth_pt":weight})
    red=(part[:,:,0]-part[:,:,1]>70)&(part[:,:,0]-part[:,:,2]>70)
    x,overall=sampled_line(red,ext,positions)
    overall[21]=1
    # A light under-stroke keeps the overall dashed line distinct at crossings.
    ax.plot(x,overall,color="white",lw=3.0,zorder=9)
    ax.plot(x,overall,color="#000000",lw=1.7,ls=(0,(5,3)),zorder=10)
    ax.axvline(mdates.date2num(np.datetime64("2022-10-01")),color=P["muted"],lw=.9)
    ax.set(xlim=(xleft,xright),ylim=(.7,1.25),yticks=[.7,.8,.9,1,1.1,1.2])
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"));ax.set_xlabel("Date",color=P["muted"],labelpad=10)
    ax.legend(handles=[Line2D([],[],color=styles[0][0],lw=styles[0][1],label="Less exposed"),Line2D([],[],color="black",lw=styles[-1][1],label="More exposed"),Line2D([],[],color="black",lw=1.7,ls=(0,(5,3)),label="Overall")],loc="lower center",bbox_to_anchor=(.5,-.34),ncol=3,frameon=False,fontsize=9,labelcolor=P["muted"])
    ax.text(.01,.95,"Ages 41–49" if older else "Ages 22–25",transform=ax.transAxes,color=P["ink"],fontweight="bold")
    save(fig,"ai-mid-career" if older else "ai-early-career","Mid Career Employment by AI Exposure" if older else "Early Career Employment by AI Exposure",[filename],"Approximate native monochrome exposure lines",out,{"source_crop_pixels":crop,"series":series,"overall":overall.tolist(),"limits":"Original exposure order retained; higher exposure uses heavier/darker strokes, overall is dashed black. Approximate monthly line centers with straight interpolation through source occlusions; not recovered empirical quintile data."})


def main():
    global PROOFS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=BOOK/"images/08_images/editorial")
    parser.add_argument("--proofs",action="store_true",help="Also export white-background PNG proofs")
    args=parser.parse_args();PROOFS=args.proofs;out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    growth(out);robot_map(out)
    retained_original("robots4.png","robot-employment","Impact of Exposure to Robots on Employment to Population Ratio")
    retained_original("robots6.png","robot-pretrends","Test of Pretrends")
    colored_scatter(out,"robots7.png","labor-share","Labor Share Decline vs. Technology Adoption",(113,80,538,521),(-6.4,10.4,-64,22),[-5,0,5,10],[-60,-40,-20,0,20],"Change in labor share · 1987–2016","Change in specialized software and dedicated machinery\nservices as a share of value added (pp)")
    colored_scatter(out,"ap.png","task-displacement","Labor Share Decline vs. Technology Adoption",(115,81,791,573),(-4.6,35.6,-24.7,64.1),[0,5,10,15,20,25,30],[-20,0,20,40,60],"Change in hourly wages · 1980–2016","Task displacement based on automation-driven\nlabor share declines, 1980–2016",multi=True)
    humlum(out);timeline(out);age_chart(out);exposure(out);exposure(out,older=True);age_chart(out,wages=True)
    assert len(RECORDS)==14
    (out/"manifest.json").write_text(json.dumps(RECORDS,indent=2))
    print(f"Created {len(RECORDS)} candidates in {out}; canonical chapter untouched.")


if __name__=="__main__":main()
