// TODO(kjlubick): use https://skia-review.googlesource.com/c/buildbot/+/134600 when it lands
export function jsonOrThrow(resp) {
  if (resp.ok) {
    return resp.json();
  }
  throw {
    message: `Bad network response: ${resp.statusText}`,
    body: resp.body,
    status: resp.status
  };
}
