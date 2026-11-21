import React from 'react';
import {Composition} from 'remotion';
import {NeonText,neonSchema} from './NeonText';
import {StoryComic,storySchema} from './StoryComic';
export const Root:React.FC=()=> <>
 <Composition id="NeonText" component={NeonText} schema={neonSchema} durationInFrames={180} fps={30} width={1280} height={720} defaultProps={{text:'Hello Story',font:'Great Vibes',color1:'#67e8f9',color2:'#f9a8d4',drawSeconds:3}}/>
 <Composition id="StoryComic" component={StoryComic} schema={storySchema} durationInFrames={180} fps={30} width={1280} height={720} calculateMetadata={({props})=>({durationInFrames:props.scenes.reduce((sum,s)=>sum+Math.round(s.seconds*30),0)})} defaultProps={{title:'Example motion comic',scenes:[{image:'demo/scene-1.svg',caption:'A small idea',seconds:2},{image:'demo/scene-2.svg',caption:'One step at a time',seconds:2},{image:'demo/scene-3.svg',caption:'A brighter day',seconds:2}]}}/>
</>;
