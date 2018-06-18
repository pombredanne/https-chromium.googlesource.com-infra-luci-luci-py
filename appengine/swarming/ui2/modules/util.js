export function stableSort(arr, comp) {
    if (!arr || !comp) {
      console.warn('missing arguments to stableSort', arr, comp);
      return;
    }
    // We can guarantee a potential non-stable sort (like V8's
    // Array.prototype.sort()) to be stable by first storing the index in the
    // original sorting and using that if the original compare was 0.
    arr.forEach((e, i) => {
      if (e !== undefined && e !== null) {
        e.__sortIdx = i;
      }
    });

    arr.sort((a, b) => {
      // undefined and null elements always go last.
      if (a === undefined || a === null) {
        if (b === undefined || b === null) {
          return 0;
        }
        return 1;
      }
      if (b === undefined || b === null) {
        return -1;
      }
      let c = comp(a, b);
      if (c === 0) {
        return a.__sortIdx - b.__sortIdx;
      }
      return c;
    });
}