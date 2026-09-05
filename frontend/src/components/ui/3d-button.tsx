import type { CSSProperties } from "react";
import { cn } from "@/lib/utils";

const letterStyle = (index: number) => ({ "--i": index } as CSSProperties);
const word = (text: string) => [...text].map((letter, index) => (
  <span data-label={letter} style={letterStyle(index + 1)} key={`${letter}-${index}`}>{letter}</span>
));

type Button3DProps = { idleLabel?: string; loadingLabel?: string };

export const Component = ({ idleLabel = "Entrar", loadingLabel = "Entrando" }: Button3DProps) => (
  <div className={cn("flex items-center justify-center py-4")}>
    <button id="btn-login" type="submit" className="button react-3d-button" aria-label="Entrar na conta">
      <div className="bg" aria-hidden="true" />
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 342 208" className="splash" aria-hidden="true">
        <path strokeLinecap="round" strokeWidth="3" d="M54.1054 99.7837S40.0984 90.7874 26.6893 97.6362 1.5 97.6362 1.5 97.6362" />
        <path strokeLinecap="round" strokeWidth="3" d="M285.273 99.7841S299.28 90.7879 312.689 97.6367 340.105 95.4893 340.105 95.4893" />
        <path strokeLinecap="round" strokeWidth="3" strokeOpacity=".3" d="M281.133 64.9917s6.827-15.1828 21.801-16.7622 16.778-11.7023 16.778-11.7023" />
        <path strokeLinecap="round" strokeWidth="3" strokeOpacity=".3" d="M281.133 138.984s6.827 15.183 21.801 16.762 16.778 11.703 16.778 11.703" />
        <path strokeLinecap="round" strokeWidth="3" d="M230.578 57.4476s-4.793-15.9425 5.483-26.9478 8.625-17.5 8.625-17.5" />
        <path strokeLinecap="round" strokeWidth="3" d="M230.578 150.528s-4.793 15.943 5.483 26.948 8.625 17.5 8.625 17.5" />
        <path strokeLinecap="round" strokeWidth="3" strokeOpacity=".3" d="M170.392 57.0278s3.498-14.8956-.821-27.4878 2.679-27.4877 2.679-27.4877" />
        <path strokeLinecap="round" strokeWidth="3" strokeOpacity=".3" d="M170.392 150.948s3.498 14.896-.821 27.488 2.679 27.488 2.679 27.488" />
        <path strokeLinecap="round" strokeWidth="3" d="M112.609 57.4476s4.792-15.9425-5.484-26.9478S98.5 12.9998 98.5 12.9998" />
        <path strokeLinecap="round" strokeWidth="3" d="M112.609 150.528s4.792 15.943-5.484 26.948-8.625 17.5-8.625 17.5" />
        <path strokeLinecap="round" strokeWidth="3" strokeOpacity=".3" d="M62.2941 64.9917S55.4671 49.8089 40.4932 48.2295 23.7159 36.5272 23.7159 36.5272" />
        <path strokeLinecap="round" strokeWidth="3" strokeOpacity=".3" d="M62.2941 145.984S55.4671 161.167 40.4932 162.746 23.7159 174.449 23.7159 174.449" />
      </svg>
      <div className="wrap" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 221 42" className="path" aria-hidden="true">
          <path strokeLinecap="round" strokeWidth="3" d="M182.674 2H203c8.837 0 16 7.163 16 16v6c0 8.837-7.163 16-16 16H18C9.163 40 2 32.837 2 24v-6C2 9.163 9.163 2 18 2h29.8855" />
        </svg>
        <div className="outline" />
        <div className="content">
          <span className="char state-1">{word(idleLabel)}</span>
          <div className="icon"><div /></div>
          <span className="char state-2">{word(loadingLabel)}</span>
        </div>
      </div>
    </button>
  </div>
);
