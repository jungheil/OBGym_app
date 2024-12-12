export interface Account {
  account: string;
  available: boolean;
}

export interface GymCampus {
  name: string;
  code: string;
}

export interface GymFacility {
  name: string;
  serviceid: string;
}

export interface GymArea {
  sname: string;
  sdate: string;
  timeno: string;
  serviceid: string;
  areaid: string;
  stockid: string;
}

export interface GroupedArea {
  timeno: string;
  areas: GymArea[];
} 