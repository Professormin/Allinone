import React, {useEffect,useMemo,useState,useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,delayRender,continueRender,cancelRender,staticFile,useCurrentFrame,useVideoConfig,interpolate} from 'remotion';
import {parse} from 'opentype.js';
import type {Font} from 'opentype.js';
import {z} from 'zod';
import {textOutlines} from './text-outlines';
export const fonts = {'Great Vibes':'GreatVibes-Regular.ttf','DM Serif Display':'DMSerifDisplay-Regular.ttf','Bebas Neue':'BebasNeue-Regular.ttf','Space Mono':'SpaceMono-Regular.ttf'};
export const neonSchema=z.object({text:z.string().trim().min(1).max(60),font:z.enum(['Great Vibes','DM Serif Display','Bebas Neue','Space Mono']),color1:z.string().regex(/^#[0-9a-fA-F]{6}$/),color2:z.string().regex(/^#[0-9a-fA-F]{6}$/),drawSeconds:z.number().min(0.5).max(5)});
type Props=z.infer<typeof neonSchema>;
export const NeonText:React.FC<Props>=(props)=>{
  const [fontMap,setFontMap]=useState<Record<string,Font>|null>(null);
  const [fontHandle]=useState(()=>delayRender('Loading outline fonts'));
  const [measureHandle]=useState(()=>delayRender('Measuring outline paths'));
  useEffect(()=>{Promise.all(Object.entries(fonts).map(async([name,file])=>{
    const response=await fetch(staticFile('fonts/'+file));
    if(!response.ok) throw new Error('Missing font: '+file);
    return [name,parse(await response.arrayBuffer())] as const;
  })).then(entries=>{setFontMap(Object.fromEntries(entries));continueRender(fontHandle);}).catch(cancelRender);},[fontHandle]);
  const frame=useCurrentFrame();const {width,height,fps}=useVideoConfig();
  const paths=useMemo(()=>{if(!props.text.trim())throw new Error('Enter visible text');return fontMap?textOutlines(fontMap[props.font],props.text.trim(),180):[];},[fontMap,props.font,props.text]);
  const svgRef=useRef<SVGSVGElement>(null);
  const [geometry,setGeometry]=useState<{lengths:number[];box:string}|null>(null);
  useLayoutEffect(()=>{
    if(!paths.length||!svgRef.current)return;
    try{
      const elements=Array.from(svgRef.current.querySelectorAll('path.measure'));
      const boxes=elements.map(p=>(p as SVGPathElement).getBBox());
      const x=Math.min(...boxes.map(b=>b.x)), y=Math.min(...boxes.map(b=>b.y));
      const right=Math.max(...boxes.map(b=>b.x+b.width)),bottom=Math.max(...boxes.map(b=>b.y+b.height));
      if(!(right>x&&bottom>y))throw new Error('Text has no drawable outline');
      setGeometry({lengths:elements.map(p=>(p as SVGPathElement).getTotalLength()),box:`${x-30} ${y-30} ${right-x+60} ${bottom-y+60}`});
      continueRender(measureHandle);
    }catch(error){cancelRender(error);}
  },[paths,measureHandle]);
  return <AbsoluteFill style={{background:'#080911',alignItems:'center',justifyContent:'center'}}>
    <svg ref={svgRef} width={width-160} height={height-160} viewBox={geometry?.box??'0 -200 1000 400'} style={{overflow:'visible'}}>
      <defs><linearGradient id="neon-gradient"><stop stopColor={props.color1}/><stop offset="1" stopColor={props.color2}/></linearGradient><filter id="neon-glow" x="-50%" y="-100%" width="200%" height="300%"><feGaussianBlur stdDeviation="3"/></filter></defs>
      {paths.map((d,i)=>{
        const progress=interpolate(frame,[i*props.drawSeconds*fps/paths.length,(i+1)*props.drawSeconds*fps/paths.length],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
        const length=geometry?.lengths[i]??1;
        return <g key={i} opacity={geometry?1:0}>
          <path className="measure" d={d} fill="none" stroke="url(#neon-gradient)" strokeWidth={6} filter="url(#neon-glow)" strokeDasharray={length} strokeDashoffset={length*(1-progress)}/>
          <path d={d} fill="none" stroke="url(#neon-gradient)" strokeWidth={1.6} strokeDasharray={length} strokeDashoffset={length*(1-progress)}/>
          <path d={d} fill="none" stroke="white" strokeWidth={0.45} strokeDasharray={length} strokeDashoffset={length*(1-progress)}/>
        </g>;
      })}
    </svg>
  </AbsoluteFill>;
};
