import React from "react";
export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body style={{margin:0,fontFamily:"system-ui",background:"#f5f5f5"}}>{children}</body></html>;
}
