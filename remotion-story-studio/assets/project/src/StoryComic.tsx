import React from 'react';
import {AbsoluteFill,CanvasImage,Sequence,staticFile,useCurrentFrame,useVideoConfig,interpolate} from 'remotion';
import {z} from 'zod';
export const storySchema=z.object({title:z.string().max(120),scenes:z.array(z.object({image:z.string(),caption:z.string().max(300),seconds:z.number().min(1).max(30)})).min(1).max(20)});
export type StoryProps=z.infer<typeof storySchema>;
const Scene:React.FC<{scene:StoryProps['scenes'][number];title:string}>=({scene,title})=>{
  const frame=useCurrentFrame();const {fps,width,height}=useVideoConfig();
  return <AbsoluteFill style={{background:'#17212b',overflow:'hidden',fontFamily:'sans-serif'}}>
    <CanvasImage src={staticFile(scene.image)} width={width} height={height} fit="cover" style={{scale:interpolate(frame,[0,scene.seconds*fps],[1,1.05],{extrapolateRight:'clamp'})}}/>
    <AbsoluteFill style={{background:'linear-gradient(transparent 55%,rgba(0,0,0,.75))'}}/>
    <div style={{position:'absolute',top:40,left:50,color:'white',fontSize:28}}>{title}</div>
    <div style={{position:'absolute',bottom:70,left:120,right:120,textAlign:'center',fontSize:48,color:'white',textShadow:'0 2px 5px black',lineHeight:1.4}}>{scene.caption}</div>
  </AbsoluteFill>;
};
export const StoryComic:React.FC<StoryProps>=({title,scenes})=>{
 const {fps}=useVideoConfig();let from=0;
 return <AbsoluteFill>{scenes.map((scene,i)=>{const start=from,duration=Math.round(scene.seconds*fps);from+=duration;return <Sequence key={i} name={'Scene-'+(i+1)} from={start} durationInFrames={duration}><Scene scene={scene} title={title}/></Sequence>;})}</AbsoluteFill>;
};
