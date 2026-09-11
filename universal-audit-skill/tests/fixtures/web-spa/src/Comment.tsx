import React from 'react';

export function Comment({ raw }: { raw: string }) {
  // renders user-submitted comment bodies
  return (
    <div
      dangerouslySetInnerHTML={{ __html: raw }}
    />
  );
}

export function SafeComment({ text }: { text: string }) {
  // NEGATIVE: escaped by React, must not be reported
  return <div>{text}</div>;
}
